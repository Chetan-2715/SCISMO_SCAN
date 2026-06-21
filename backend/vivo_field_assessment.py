import cv2
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier

# 1. VIVO PHONE OPTICAL CALIBRATION WITH EXACT DISTANCE
def calculate_vivo_gsd(distance_from_wall_mm, focal_length_mm=4.3, sensor_height_mm=4.6, image_height_px=4000):
    """Calculates mm/pixel multiplier tailored specifically for your Vivo phone camera sensor."""
    gsd = (distance_from_wall_mm * sensor_height_mm) / (focal_length_mm * image_height_px)
    return gsd

# 2. ADAPTIVE FILTERING FOR MOBILE LIGHTING & SHADOWS
def preprocess_vivo_photo(image_path):
    """Cleans up harsh lighting, shadows, and plaster textures from smartphone photos."""
    # os.path.normpath cleans up conflicting slashes automatically for Windows
    clean_path = os.path.normpath(image_path)
    img = cv2.imread(clean_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
        
    # Resize if image is extremely large to maintain processing speeds
    if img.shape[0] > 2000 or img.shape[1] > 2000:
        scale_percent = 50
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        
    # Cancel out shadows using advanced CLAHE
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(12,12))
    enhanced_img = clahe.apply(img)
    
    # Smooth rough surface textures while keeping crack boundaries sharp
    filtered_img = cv2.bilateralFilter(enhanced_img, d=11, sigmaColor=85, sigmaSpace=85)
    
    # Convert to pure binary mask
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
    
    # Real-world mm conversions
    crack_length_mm = pixel_length * gsd
    crack_width_mm = pixel_width * gsd
    
    permissible_limit = 0.2 if environment == "Outdoor" else 0.3
    
    if crack_width_mm <= permissible_limit:
        severity = "Low (Safe under IS 456 limits)"
        repair = "Surface sealing & weather-proof finishing (IS 15988 Cl 8.1)"
    elif crack_width_mm <= 1.0:
        severity = "Moderate (Exceeds Durability Thresholds)"
        repair = "Pressure epoxy injection grouting (IS 15988 Cl 8.1.1.1)"
    else:
        severity = "Severe Structural Distress (Immediate Collapse Risk)"
        repair = "RC/FRP Structural Column Jacketing (IS 15988 Cl 8.4)"
        
    return crack_length_mm, crack_width_mm, severity, repair

# 4. TRAINING BASE SEISMIC BRAIN
def train_seismic_classifier():
    X = np.array([[0.1, 20.0, 2, 4], [0.3, 60.0, 2, 4], [0.6, 140.0, 2, 4], [1.3, 320.0, 2, 4], [2.2, 550.0, 2, 4]])
    y = np.array([0, 0, 1, 1, 2])
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    return clf

# 5. LIVE EXECUTION ENGINE FOR A SINGLE FIELD PHOTO
if __name__ == "__main__":
    print("====================================================")
    print("   VIVO SMARTPHONE - SINGLE TEST SAMPLE PIPELINE    ")
    print("====================================================\n")
    
    # Standing 1.5 meters away from the structure
    vivo_distance_mm = 1500  
    
    # Image name setup
    test_image_name = "site_test1.jpeg" 
    
    # Windows-compliant path construction
    full_image_path = os.path.join("Images", test_image_name)
    
    # Run calibration and load predictive model
    gsd_scale = calculate_vivo_gsd(distance_from_wall_mm=vivo_distance_mm)
    brain = train_seismic_classifier()
    
    print(f"[INFO] Processing sample image: {full_image_path}...")
    mask = preprocess_vivo_photo(full_image_path)
    
    if mask is None:
        print(f"\n[ERROR] '{full_image_path}' not found! Please check that 'site_test1.jpg' is located inside your 'Images' folder.")
    else:
        c_length, c_width, c_severity, c_repair = analyze_vivo_crack(mask, gsd_scale, environment="Outdoor")
        safety_code = brain.predict(np.array([[c_width, c_length, 2, 4]]))
        tag_lib = {0: "GREEN (Safe)", 1: "YELLOW (Restricted)", 2: "RED (Danger)"}
        
        # Display the formal Indian Standard evaluation dashboard
        print(f"\n================ TEST IMAGE FIELD REPORT ================")
        print(f"File Name       : {test_image_name}")
        print(f"Calculated Width: {c_width:.2f} mm")
        print(f"Calculated Length: {c_length:.2f} mm")
        print(f"IS 456 Status   : {c_severity}")
        print(f"IS 15988 Repair : {c_repair}")
        print(f"Seismic Rating  : {tag_lib[safety_code[0]]}")
        print("=========================================================\n")
