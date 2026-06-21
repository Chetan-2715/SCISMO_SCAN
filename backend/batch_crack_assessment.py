import cv2
import numpy as np
import os
import pandas as pd

# 1. SDNET2018 NATIVE CALIBRATION
def calculate_gsd(distance_mm=500, focal_length_mm=4.3, sensor_height_mm=4.6, image_height_px=4000):
    return (distance_mm * sensor_height_mm) / (focal_length_mm * image_height_px)

# 2. IMAGE PREPROCESSING (SUPPRESS CONCRETE SURFACE NOISE)
def preprocess_sdnet_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_img = clahe.apply(img)
    filtered_img = cv2.bilateralFilter(enhanced_img, d=9, sigmaColor=50, sigmaSpace=50)
    binary_crack_mask = cv2.adaptiveThreshold(
        filtered_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 6
    )
    return binary_crack_mask

# 3. DUAL-CLASS ENGINEERING ENGINES WITH YOUR CUSTOM TAGS
def analyze_sdnet_geometry(binary_mask, gsd, environment="Outdoor"):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # Baseline condition: Perfectly clean surface
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
        
        if pixel_length > 30 and pixel_area > 80:
            bx, by, bw, bh = cv2.boundingRect(main_contour)
            aspect_ratio = max(bw, bh) / min(max(1, bw), max(1, bh))
            
            if aspect_ratio > 1.8:
                is_cracked = True
                pixel_width = pixel_area / pixel_length if pixel_length > 0 else 0
                crack_length_mm = pixel_length * gsd
                crack_width_mm = pixel_width * gsd
                
                permissible_limit = 0.2 if environment == "Outdoor" else 0.3
                
                # STRICT MAPPING WITH BLUE LOW SEVERITY RULE
                if crack_width_mm <= permissible_limit:
                    severity = "Low"
                    repair = "Surface sealing (IS 15988 Cl 8.1)"
                    safety_tag = "BLUE (Minor Distress)" # Custom Blue Category Applied
                elif crack_width_mm <= 1.0:
                    severity = "Moderate"
                    repair = "Epoxy injection (IS 15988 Cl 8.1.1.1)"
                    safety_tag = "YELLOW (Restricted)"
                else:
                    severity = "Severe"
                    repair = "RC/FRP Structural Jacketing (IS 15988 Cl 8.4)"
                    safety_tag = "RED (Danger)"
                    
    return is_cracked, crack_length_mm, crack_width_mm, severity, repair, safety_tag

# 4. AUTOMATED BATCH ENGINE FOR REPOS
if __name__ == "__main__":
    print("==========================================================")
    print("     SDNET2018 DUAL-CLASS BATCH DECK PROCESSOR            ")
    print("==========================================================\n")
    
    target_folder = r"Dataset\Decks\Cracked"
    sdnet_gsd = calculate_gsd(distance_mm=500)
    
    if not os.path.exists(target_folder):
        print(f"[ERROR] Folder path '{target_folder}' not found!")
        exit()
        
    image_files = [f for f in os.listdir(target_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    print(f"[INFO] Scanning directory. Found {len(image_files)} concrete specimens.\n")
    
    results_list = []
    
    for img_name in image_files:
        full_path = os.path.join(target_folder, img_name)
        mask = preprocess_sdnet_image(full_path)
        if mask is None:
            continue
            
        has_crack, length, width, severity, repair, safety_tag = analyze_sdnet_geometry(mask, sdnet_gsd, environment="Outdoor")
        
        status_text = "Cracked" if has_crack else "No Crack Detected"
        print(f"File: {img_name} | Width: {width:.2f}mm | Class: {severity} | Tag: {safety_tag}")
        
        results_list.append({
            "Specimen Name": img_name,
            "Surface Evaluation": status_text,
            "Calculated Length (mm)": round(length, 2),
            "Calculated Width (mm)": round(width, 2),
            "IS 456 Severity Class": severity,
            "IS 15988 Repair Method": repair,
            "Predicted Seismic Tag": safety_tag
        })
    
    df = pd.DataFrame(results_list)
    df.to_csv("structural_assessment_report.csv", index=False)
    print("\n[SUCCESS] Batch run complete. Logs saved to 'structural_assessment_report.csv'")
