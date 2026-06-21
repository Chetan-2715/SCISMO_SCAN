import cv2
import numpy as np
import os
import pandas as pd
from ultralytics import YOLO

# 1. OPTICAL CALIBRATION TRIGONOMETRY
def calculate_gsd(distance_mm, focal_length_mm=4.3, sensor_height_mm=4.6, image_height_px=4000):
    """Calculates mm/pixel scale factor for the camera sensor matrix."""
    return (distance_mm * sensor_height_mm) / (focal_length_mm * image_height_px)

# 2. OBJECT DETECTION LAYER USING PRE-TRAINED YOLOv8 (FIXED FOR ULTRALYTICS LIST OUTPUT)
def run_yolo_component_detector(image_path, model):
    img = cv2.imread(image_path)
    if img is None: 
        return None, []
    
    results = model(img, verbose=False)
    cropped_regions = []
    
    # 🎯 FIX: Extract the first Result object from the output list safely
    if results and len(results) > 0:
        first_result = results[0]
        # Extract regional structural bounding matrices from YOLO coordinate arrays
        for idx, box in enumerate(first_result.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = img[y1:y2, x1:x2]
            cropped_regions.append((f"yolo_region_{idx}", crop))
        
    if not cropped_regions:
        cropped_regions.append(("detected_concrete_element", img))
        
    return img, cropped_regions

# 3. ADVANCED FAULT SEGMENTATION FILTER
def preprocess_concrete_crop(crop_img):
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
    filtered = cv2.bilateralFilter(clahe, d=9, sigmaColor=50, sigmaSpace=50)
    binary_mask = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 6
    )
    return binary_mask

# 4. DUAL-CLASS ENGINEERING ENGINES WITH YOUR CUSTOM TAGS
def analyze_cropped_geometry(binary_mask, gsd, environment="Outdoor"):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    is_cracked = False
    crack_length_mm = 0.0
    crack_width_mm = 0.0
    severity = "No Crack Detected"
    repair = "No Action Required"
    safety_tag = "GREEN (Safe)"
    
    if contours:
        main_contour = max(contours, key=cv2.contourArea)
        pixel_area = cv2.contourArea(main_contour)
        pixel_length = cv2.arcLength(main_contour, closed=False) / 2.0
        
        # 🛡️ VALIDATION GATE: Filter out random background concrete noise
        if pixel_length > 30 and pixel_area > 80:
            bx, by, bw, bh = cv2.boundingRect(main_contour)
            aspect_ratio = max(bw, bh) / min(max(1, bw), max(1, bh))
            
            if aspect_ratio > 1.8:
                is_cracked = True
                pixel_width = pixel_area / pixel_length if pixel_length > 0 else 0
                crack_length_mm = pixel_length * gsd
                crack_width_mm = pixel_width * gsd
                
                permissible_limit = 0.2 if environment == "Outdoor" else 0.3
                
                if crack_width_mm <= permissible_limit:
                    severity = "Low"
                    repair = "Surface sealing (IS 15988 Cl 8.1)"
                    safety_tag = "BLUE (Minor Distress)"
                elif crack_width_mm <= 1.0:
                    severity = "Moderate"
                    repair = "Epoxy injection (IS 15988 Cl 8.1.1.1)"
                    safety_tag = "YELLOW (Restricted)"
                else:
                    severity = "Severe"
                    repair = "RC/FRP Structural Jacketing (IS 15988 Cl 8.4)"
                    safety_tag = "RED (Danger)"
                    
    return is_cracked, crack_length_mm, crack_width_mm, severity, repair, safety_tag

# 5. AUTOMATED INTEGRATED DATASET PIPELINE
if __name__ == "__main__":
    print("====================================================")
    print("   UNIFIED HYBRID YOLOv8 MULTI-DATASET BALANCER     ")
    print("====================================================\n")
    
    yolo_net = YOLO("yolov8n.pt")
    hybrid_records = []
    
    # 📋 MASTER DEFINITION FOR RUNNING BOTH DATASETS CONCURRENTLY
    datasets_to_process = [
        {
            "name": "SDNET2018 Dataset",
            "folder": r"Dataset\Decks\Cracked",
            "distance": 500,        
            "max_images": 30        
        },
        {
            "name": "Real-Field Smartphone Photos",
            "folder": r"Images",
            "distance": 300,        
            "max_images": 0         
        }
    ]
    
    for target in datasets_to_process:
        print(f"--> Initiating sweep for: {target['name']}")
        current_folder = target["folder"]
        
        if not os.path.exists(current_folder):
            print(f"    [WARNING] Folder path '{current_folder}' not found. Skipping.\n")
            continue
            
        image_files = [f for f in os.listdir(current_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        
        if target["max_images"] > 0:
            image_files = image_files[:target["max_images"]]
            
        gsd_multiplier = calculate_gsd(distance_mm=target["distance"])
        
        for idx, filename in enumerate(image_files, 1):
            full_path = os.path.join(current_folder, filename)
            original_image, detected_crops = run_yolo_component_detector(full_path, yolo_net)
            
            if original_image is None: 
                continue
                
            for name, crop in detected_crops:
                mask = preprocess_concrete_crop(crop)
                has_crack, length, width, severity, repair, safety_tag = analyze_cropped_geometry(mask, gsd_multiplier)
                
                status_text = "Cracked" if has_crack else "No Crack Detected"
                print(f"    [{idx}/{len(image_files)}] File: {filename} | Width: {width:.2f}mm | Tag: {safety_tag}")
                
                hybrid_records.append({
                    "Data Group Source": target["name"],
                    "Image Filename": filename,
                    "YOLO Bounding ID": name,
                    "Surface State": status_text,
                    "True Width (mm)": round(width, 2),
                    "True Length (mm)": round(length, 2),
                    "IS 456 Severity Class": severity,
                    "IS 15988 Repair Method": repair,
                    "Assigned Structural Tag": safety_tag
                })
        print(f"✓ Completed {target['name']} processing segment.\n")
        
    # Export combined records to a single master data sheet
    if hybrid_records:
        df_master = pd.DataFrame(hybrid_records)
        output_csv = "master_hybrid_yolo_report.csv"
        df_master.to_csv(output_csv, index=False)
        print("====================================================")
        print(f"[SUCCESS] Unified multi-dataset execution complete!")
        print(f"Master file saved cleanly as: '{output_csv}'")
        print("====================================================")
