import os
import cv2
import numpy as np

# ==============================================================================
# YOLO MODEL INITIALIZATION
# ==============================================================================
try:
    from ultralytics import YOLO
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "best_structural_model.pt")
    if os.path.exists(model_path):
        model = YOLO(model_path)
        print(f"Success: YOLO Model loaded from: {model_path}")
    else:
        print(f"Warning: Model not found at {model_path}. Structural element detection disabled.")
        model = None
except Exception as e:
    print(f"YOLO load error: {e}")
    model = None


def estimate_crack_depth(width_mm, element_type="Wall/Pavement"):
    """
    Empirical depth estimation based on IS 456:2000 cover requirements and crack width.
    - Column: 40mm nominal cover
    - Beam: 25mm nominal cover
    - Slab: 20mm nominal cover
    - Wall/Pavement: 20mm nominal cover
    """
    if element_type == "Column":
        cover = 40.0
        if width_mm <= 0.2:
            depth = min(15.0, width_mm * 75.0)
        elif width_mm <= 0.4:
            depth = cover
        else:
            depth = cover + (width_mm - 0.4) * 80.0
            depth = min(depth, 150.0) # Cap at typical column reinforcement depth limit
    elif element_type == "Beam":
        cover = 25.0
        if width_mm <= 0.2:
            depth = min(10.0, width_mm * 50.0)
        elif width_mm <= 0.4:
            depth = cover
        else:
            depth = cover + (width_mm - 0.4) * 60.0
            depth = min(depth, 100.0) # Cap at typical beam reinforcement depth limit
    elif element_type == "Slab":
        cover = 20.0
        if width_mm <= 0.2:
            depth = min(8.0, width_mm * 40.0)
        elif width_mm <= 0.4:
            depth = cover
        else:
            depth = cover + (width_mm - 0.4) * 40.0
            depth = min(depth, 50.0) # Cap at slab half-thickness
    else:  # Wall / Pavement / Deck / General
        cover = 20.0
        if width_mm <= 0.2:
            depth = min(8.0, width_mm * 40.0)
        elif width_mm <= 0.4:
            depth = cover
        else:
            depth = cover + (width_mm - 0.4) * 50.0
            depth = min(depth, 60.0)
    return round(depth, 2)


def detect_multiple_cracks_end_to_end(image_path, capture_distance_mm=300, element_type="Auto", calibration_line=None, calibration_length_mm=None):
    img = cv2.imread(image_path)
    if img is None:
        return None, None, 0, 0.0, 0.0, 0.0, "Error", "Input frame path not found.", []

    output_img = img.copy()

    h, w = img.shape[:2]
    
    # Calculate PPM:
    # If a calibration line is drawn, use it; otherwise fallback to capture distance
    if calibration_line and calibration_length_mm:
        try:
            parts = [float(x) for x in calibration_line.split(",")]
            if len(parts) == 4:
                nx1, ny1, nx2, ny2 = parts
                x1, y1 = int(nx1 * w), int(ny1 * h)
                x2, y2 = int(nx2 * w), int(ny2 * h)
                
                # Compute distance in pixels
                pixel_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if pixel_length > 0 and calibration_length_mm > 0:
                    ppm = pixel_length / calibration_length_mm
                    print(f"[INFO] Calibrated PPM to {ppm:.3f} using user line length {calibration_length_mm} mm.")
                    
                    # Draw the pink/magenta line on the output image (thickness 3)
                    cv2.line(output_img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    # Add a text label above it
                    cv2.putText(output_img, f"{calibration_length_mm}mm Scale", (min(x1, x2), max(15, min(y1, y2) - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2, cv2.LINE_AA)
                else:
                    ppm = w / capture_distance_mm
            else:
                ppm = w / capture_distance_mm
        except Exception as e:
            print(f"Error parsing calibration line: {e}")
            ppm = w / capture_distance_mm
    else:
        ppm = w / capture_distance_mm

    detected_elements = []
    total_cracks_found = 0
    max_overall_width = 0.0
    total_crack_length = 0.0
    max_overall_depth = 0.0
    crack_details_list = []

    yolo_mask = np.zeros((h, w), dtype=np.uint8)

    # STEP 1: Run YOLOv8 Segmentation to locate the cracks
    if model is not None:
        try:
            results = model(img, conf=0.45)
            for result in results:
                # Process segmentation masks
                if result.masks is not None:
                    for xy in result.masks.xy:
                        if len(xy) > 0:
                            polygon = np.array(xy, dtype=np.int32)
                            cv2.fillPoly(yolo_mask, [polygon], 255)
        except Exception as e:
            print(f"YOLO segmentation mask extraction error: {e}")

    # Use auto-detection if set to "Auto"
    if element_type == "Auto" or element_type == "Auto Detect":
        element_type = "Wall/Pavement"

    # STEP 2: OpenCV crack detection with YOLO gating mask
    output_img, binary_mask, total_cracks_found, max_overall_width, total_crack_length, max_overall_depth, crack_details_list = \
        process_highly_accurate_cracks(
            img, ppm, output_img,
            total_cracks_found, max_overall_width, total_crack_length, crack_details_list, element_type, yolo_mask
        )

    severity, workflow = evaluate_structural_status(max_overall_width, total_cracks_found, detected_elements)

    return output_img, binary_mask, total_cracks_found, max_overall_width, total_crack_length, max_overall_depth, severity, workflow, crack_details_list


def detect_text_regions(img, global_thresh):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    text_mask = np.zeros((h, w), dtype=np.uint8)

    mser = cv2.MSER_create(delta=5, min_area=30, max_area=3000)
    regions, _ = mser.detectRegions(gray)
    for region in regions:
        hull = cv2.convexHull(region.reshape(-1, 1, 2))
        
        # Check overlap with global_thresh to avoid masking out true crack voids
        region_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(region_mask, [hull], -1, 255, -1)
        overlap = cv2.bitwise_and(region_mask, global_thresh)
        if np.sum(overlap) > 0:
            continue
            
        cv2.fillPoly(text_mask, [hull], 255)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    text_mask = cv2.dilate(text_mask, kernel, iterations=1)

    return text_mask


def process_highly_accurate_cracks(img, ppm, output_img, count, max_w, total_l, details, element_type, yolo_mask=None):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 1. Smooth textures using a Bilateral Filter while maintaining crack boundary sharpness
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    filtered = cv2.bilateralFilter(enhanced, d=9, sigmaColor=50, sigmaSpace=50)

    # Global threshold for deep wide black gaps
    _, global_thresh = cv2.threshold(filtered, 75, 255, cv2.THRESH_BINARY_INV)

    # Detect text regions, gated by global_thresh to avoid blanking out the crack
    text_mask = detect_text_regions(img, global_thresh)

    # 2. Adaptive threshold path
    thresh = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 20
    )
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_adapt = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close, iterations=1)
    cleaned_adapt = cv2.bitwise_and(cleaned_adapt, cv2.bitwise_not(text_mask))

    # 3. Global threshold path
    cleaned_global = cv2.bitwise_and(global_thresh, cv2.bitwise_not(text_mask))

    yolo_active = yolo_mask is not None and np.sum(yolo_mask) > 0

    # Gate the masks with yolo_mask if YOLO detected cracks, to prevent noise from merging
    if yolo_active:
        cleaned_adapt = cv2.bitwise_and(cleaned_adapt, yolo_mask)
        cleaned_global = cv2.bitwise_and(cleaned_global, yolo_mask)

    def get_valid_contours(cleaned_mask):
        valid_list = []
        contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0 or area == 0:
                continue

            circularity = (4 * np.pi * area) / (perimeter ** 2)
            rx, ry, rw, rh = cv2.boundingRect(contour)
            side_long  = max(rw, rh)
            side_short = min(rw, rh)
            aspect_ratio = side_long / side_short if side_short > 0 else 0

            # Standard structural crack filters (relaxed if YOLO has pre-validated the region)
            min_ar = 1.3 if yolo_active else 1.5
            min_area = 50 if yolo_active else 80
            min_perim = 35 if yolo_active else 50
            max_circ = 0.6 if yolo_active else 0.5

            if not (circularity < max_circ and area > min_area and perimeter > min_perim
                    and aspect_ratio > min_ar and rw < 0.9 * w):
                continue

            valid_list.append(contour)
        return valid_list

    # Find valid contours for both paths
    global_contours = get_valid_contours(cleaned_global)

    # Check if we have a significant wide crack in global threshold
    has_significant_wide_crack = any(cv2.contourArea(c) > 150 for c in global_contours)

    if has_significant_wide_crack:
        print("[INFO] Significant wide crack detected. Using clean global threshold mask.")
        final_contours = global_contours
        binary_mask = cleaned_global
    else:
        print("[INFO] No wide crack detected. Falling back to adaptive threshold mask.")
        final_contours = get_valid_contours(cleaned_adapt)
        binary_mask = cleaned_adapt

    max_d = 0.0

    for contour in final_contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0 or area == 0:
            continue

        count += 1
        rx, ry, rw, rh = cv2.boundingRect(contour)
        rect = cv2.minAreaRect(contour)
        (cx, cy), (w_px, h_px), angle = rect

        # Calculate physical dimensions robustly using Area / Bounding Box Length
        length_px = max(w_px, h_px)
        width_px  = area / length_px if length_px > 0 else 0.0

        c_width_mm  = round(max(width_px  / ppm, 0.01), 2)
        c_length_mm = round(max(length_px / ppm, 0.01), 2)
        c_depth_mm  = estimate_crack_depth(c_width_mm, element_type)

        total_l += c_length_mm
        if c_width_mm > max_w:
            max_w = c_width_mm
        if c_depth_mm > max_d:
            max_d = c_depth_mm

        cv2.drawContours(output_img, [contour], -1, (0, 255, 0), 2)
        cv2.rectangle(output_img, (rx, ry), (rx + rw, ry + rh), (0, 0, 255), 2)

        label = f"C{count}: {c_width_mm:.1f}mm|D:{c_depth_mm:.1f}mm"
        cv2.putText(output_img, label, (rx, max(15, ry - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 255), 1, cv2.LINE_AA)

        details.append({
            "id":     count,
            "width":  c_width_mm,
            "length": c_length_mm,
            "depth":  c_depth_mm
        })

    return output_img, binary_mask, count, max_w, total_l, max_d, details


def evaluate_structural_status(max_width, total_cracks, elements):
    if total_cracks == 0:
        return (
            "Safe (No Structural Defects Found)",
            "-> Structure is structurally sound.\nNo remedial repair action required under IS 15988 / IS 456 guidelines."
        )

    has_column = any(el["class"] == "Column" for el in elements)
    has_beam   = any(el["class"] == "Beam"   for el in elements)

    if max_width <= 0.2:
        severity = "Low (Permissible Hairline Distress)"
        workflow = (
            "-> IS 15988 Cl 8.1 Repair Workflow:\n"
            "Surface cleaning & weather-proof elastomeric protective layer application."
        )
    elif max_width <= 0.4:
        severity = "Medium (Structural Distress — Initial Stage)"
        if has_column:
            workflow = (
                "-> IS 15988 Cl 8.2 Repair Workflow (Column):\n"
                "Low-viscosity structural Epoxy Injection Grouting under pressure "
                "to restore concrete monolithic bond."
            )
        else:
            workflow = (
                "-> IS 15988 Cl 8.2 Repair Workflow (Beam/Slab):\n"
                "Pressure Grouting utilizing standard low-viscosity structural epoxies."
            )
    else:
        severity = "High (Critical Structural Damage — Urgent Action Needed)"
        if has_column:
            workflow = (
                "-> IS 15988 Cl 8.5.1 Repair Workflow (CRITICAL COLUMN):\n"
                "Immediate Section Enlargement / RCC Jacketing required. "
                "Install confinement steel wire ties (@100mm pitch) with min 100mm "
                "micro-concrete jacket encapsulation."
            )
        elif has_beam:
            workflow = (
                "-> IS 15988 Cl 8.5 Repair Workflow (CRITICAL BEAM):\n"
                "Flexural strengthening via Carbon Fiber Reinforced Polymer (CFRP) "
                "composite wrapping or epoxy-bonded structural steel plate attachments."
            )
        else:
            workflow = (
                "-> Mechanical structural stitching using rebar anchors, followed by "
                "high-strength Polymer Modified Mortar (PMM) packing."
            )

    return severity, workflow