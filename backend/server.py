import os
import cv2
import base64
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crack_processor import detect_multiple_cracks_end_to_end

app = FastAPI(title="Structural Damage Assessment API", version="1.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def encode_img_to_base64(img_ndarray):
    """Encodes a BGR/Grayscale opencv image to a base64 string."""
    if img_ndarray is None:
        return ""
    success, buffer = cv2.imencode('.png', img_ndarray)
    if not success:
        return ""
    return "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')

@app.post("/api/process")
async def process_specimen(
    file: UploadFile = File(...),
    capture_distance_mm: int = Form(300),
    element_type: str = Form("Auto"),
    calibration_line: str = Form(None),
    calibration_length_mm: float = Form(None)
):
    try:
        # Read uploaded image bytes
        file_bytes = await file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image format.")
            
        # Write to temporary file for the path-based backend function
        temp_filename = f"temp_upload_{file.filename}"
        cv2.imwrite(temp_filename, img)
        
        try:
            # Execute assessment pipeline
            out_img, mask_img, total_cnt, max_w, total_l, max_d, severity, workflow, logs = \
                detect_multiple_cracks_end_to_end(
                    temp_filename, 
                    capture_distance_mm, 
                    element_type, 
                    calibration_line, 
                    calibration_length_mm
                )
        except Exception as inner_e:
            print(f"Error inside processing pipeline: {inner_e}")
            raise HTTPException(status_code=500, detail=f"Pipeline error: {str(inner_e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
        if out_img is None:
            raise HTTPException(status_code=500, detail="Backend failed to process concrete image.")
            
        # Base64 encode the output images
        annotated_b64 = encode_img_to_base64(out_img)
        mask_b64 = encode_img_to_base64(mask_img)
        
        return {
            "success": True,
            "filename": file.filename,
            "total_cracks": total_cnt,
            "max_width_mm": max_w,
            "total_length_mm": total_l,
            "max_depth_mm": max_d,
            "severity": severity,
            "workflow": workflow,
            "element_type_evaluated": element_type,
            "crack_logs": logs,
            "visual_assets": {
                "annotated_b64": annotated_b64,
                "mask_b64": mask_b64
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def healthcheck():
    return {"status": "healthy", "service": "crack-processor-backend"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
