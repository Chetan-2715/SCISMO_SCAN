import cv2
import numpy as np
import os
import pandas as pd

def compile_academic_visual_panels(csv_path):
    print("--- Initiating Structural Visual Panel Compilation Engine ---")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} database not found! Run your batch code first.")
        return
        
    df = pd.read_csv(csv_path)
    output_dir = "Results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard color map matrix definitions (BGR format for OpenCV)
    color_map = {
        "GREEN (Safe)": (46, 204, 113),       # Emerald Green
        "BLUE (Minor Distress)": (219, 152, 52), # Deep Cobalt Blue 
        "YELLOW (Restricted)": (15, 196, 241),  # Sun Orange-Yellow
        "RED (Danger)": (60, 76, 231)          # Dark Warning Crimson Red
    }
    
    # Loop through rows to compile visual comparison strips
    for idx, row in df.iterrows():
        # Check filename across multiple folders automatically
        img_name = row.iloc[0]
        possible_paths = [
            os.path.join("Images", img_name),
            os.path.join("Dataset", "Decks", "Cracked", img_name),
            os.path.join("Dataset", "Decks", "Non-cracked", img_name)
        ]
        
        src_path = None
        for p in possible_paths:
            if os.path.exists(p):
                src_path = p
                break
                
        if src_path is None:
            continue
            
        # 1. Read Original Specimen
        orig = cv2.imread(src_path)
        if orig is None: continue
        orig = cv2.resize(orig, (400, 400))
        
        # 2. Compute Segmented Mask Matrix
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
        filtered = cv2.bilateralFilter(clahe, d=9, sigmaColor=50, sigmaSpace=50)
        mask = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 6)
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # 3. Compile the Engineering Evaluation Overlay Panel Layer
        overlay_panel = orig.copy()
        tag = row.get("Predicted Seismic Tag", "GREEN (Safe)")
        current_color = color_map.get(tag, (127, 127, 127))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours and "No Crack" not in str(row.iloc[1]):
            main_cnt = max(contours, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(main_cnt)
            # Draw tracking boundary coordinates
            cv2.rectangle(overlay_panel, (bx, by), (bx + bw, by + bh), current_color, 4)
            cv2.drawContours(overlay_panel, [main_cnt], -1, (255, 0, 0), 2)
            
        # Draw a clean HUD text bar at the top of the image strip panel
        cv2.rectangle(overlay_panel, (0, 0), (400, 50), (30, 30, 30), -1)
        cv2.putText(overlay_panel, f"TAG: {tag.split(' ')[0]}", (15, 33), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, current_color, 2, cv2.LINE_AA)
                    
        # 4. Concatenate horizontally to build a single comprehensive research strip panel
        compiled_strip = np.hstack([orig, mask_bgr, overlay_panel])
        
        # Save compiled structural panel to disk
        out_name = f"panel_{os.path.splitext(img_name)[0]}.png"
        cv2.imwrite(os.path.join(output_dir, out_name), compiled_strip)
        print(f"[COMPILED] Visual Research Grid Panel Saved: {out_name}")
        
    print(f"\n[SUCCESS] All structural visual grids compiled cleanly inside your 'Results/' directory!")

if __name__ == "__main__":
    # 📊 PANEL 1: Compile visual research strips for SDNET2018 dataset
    print("\n>>> Processing SDNET2018 Dataset Image Folders...")
    compile_academic_visual_panels("structural_assessment_report.csv")
    
    # 📱 PANEL 2: Compile visual research strips for Smartphone Site Photos
    print("\n>>> Processing Real-World Smartphone Site Photos...")
    compile_academic_visual_panels("real_field_assessment_report.csv")
