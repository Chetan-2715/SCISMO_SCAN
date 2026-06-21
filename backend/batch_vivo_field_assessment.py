import cv2
import numpy as np
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. VIVO PHONE OPTICAL CALIBRATION WITH EXACT DISTANCE
def calculate_vivo_gsd(distance_from_wall_mm, focal_length_mm=4.3, sensor_height_mm=4.6, image_height_px=4000):
    gsd = (distance_from_wall_mm * sensor_height_mm) / (focal_length_mm * image_height_px)
    return gsd

# 2. ADAPTIVE FILTERING FOR MOBILE LIGHTING & SHADOWS
def preprocess_vivo_photo(image_path):
    clean_path = os.path.normpath(image_path)
    img = cv2.imread(clean_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
        
    if img.shape[0] > 2000 or img.shape[1] > 2000:
        scale_percent = 50
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(12,12))
    enhanced_img = clahe.apply(img)
    filtered_img = cv2.bilateralFilter(enhanced_img, d=11, sigmaColor=85, sigmaSpace=85)
    
    binary_mask = cv2.adaptiveThreshold(
        filtered_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 5
    )
    return binary_mask

# 3. IS 456:2000 CRACK WIDTH QUANTIFICATION ENGINE
def analyze_vivo_crack(binary_mask, gsd, environment="Outdoor"):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return 0.0, 0.0, "No Active Crack Found", "No Structural Action Required"
        
    main_contour = max(contours, key=cv2.contourArea)
    pixel_length = cv2.arcLength(main_contour, closed=False) / 2.0
    pixel_area = cv2.contourArea(main_contour)
    pixel_width = pixel_area / pixel_length if pixel_length > 0 else 0
    
    crack_length_mm = pixel_length * gsd
    crack_width_mm = pixel_width * gsd
    permissible_limit = 0.2 if environment == "Outdoor" else 0.3
    
    if crack_width_mm <= permissible_limit:
        severity = "Low"
        repair = "Surface sealing (IS 15988 Cl 8.1)"
    elif crack_width_mm <= 1.0:
        severity = "Moderate"
        repair = "Pressure epoxy injection (IS 15988 Cl 8.1.1.1)"
    else:
        severity = "Severe"
        repair = "RC/FRP Structural Jacketing (IS 15988 Cl 8.4)"
        
    return crack_length_mm, crack_width_mm, severity, repair

# 4. TRAINING BASE SEISMIC BRAIN
def train_seismic_classifier():
    X = np.array([[0.1, 20.0, 2, 4], [0.3, 60.0, 2, 4], [0.6, 140.0, 2, 4], [1.3, 320.0, 2, 4], [2.2, 550.0, 2, 4]])
    y = np.array([0, 0, 1, 1, 2])
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    return clf

# 5. AUTOMATED BATCH ENGINE FOR FIELD IMAGES FOLDER
if __name__ == "__main__":
    print("====================================================")
    print("      VIVO SMARTPHONE BATCH FIELD PROCESSING        ")
    print("====================================================\n")
    
    vivo_distance_mm = 1500  
    field_folder = "Images"
    
    gsd_scale = calculate_vivo_gsd(distance_from_wall_mm=vivo_distance_mm)
    brain = train_seismic_classifier()
    
    if not os.path.exists(field_folder):
        print(f"Error: Folder '{field_folder}' not found!")
        exit()
        
    all_field_images = [f for f in os.listdir(field_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    print(f"[INFO] Discovered {len(all_field_images)} site photos inside Images/ folder.\n")
    
    field_records = []
    tag_lib = {0: "GREEN (Safe)", 1: "YELLOW (Restricted)", 2: "RED (Danger)"}
    
    for filename in all_field_images:
        path = os.path.join(field_folder, filename)
        mask = preprocess_vivo_photo(path)
        if mask is None:
            continue
            
        c_length, c_width, c_severity, c_repair = analyze_vivo_crack(mask, gsd_scale, environment="Outdoor")
        safety_code = brain.predict(np.array([[c_width, c_length, 2, 4]]))
        
        print(f"File: {filename} | Width: {c_width:.2f}mm | Length: {c_length:.2f}mm | Risk: {tag_lib[safety_code[0]]}")
        
        field_records.append({
            "Site Image File": filename,
            "Measured Length (mm)": round(c_length, 2),
            "Measured Width (mm)": round(c_width, 2),
            "IS 456 Severity Class": c_severity,
            "IS 15988 Field Remediation": c_repair,
            "Predicted Seismic Tag": tag_lib[safety_code[0]]
        })
        
    df_field = pd.DataFrame(field_records)
    df_field.to_csv("real_field_assessment_report.csv", index=False)
    print("\n[SUCCESS] Field metrics logged to 'real_field_assessment_report.csv'!")
