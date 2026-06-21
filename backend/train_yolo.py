import os
import yaml
from ultralytics import YOLO

def main():
    # 1. Dynamically resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__)) # D:\CIVIL PROJECT\backend
    project_root = os.path.dirname(script_dir)             # D:\CIVIL PROJECT
    dataset_dir = os.path.join(project_root, "dataset")    # D:\CIVIL PROJECT\dataset

    # 2. Check if dataset folder exists
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f"Error: Dataset folder not found at '{dataset_dir}'. Please place the dataset folder in the project root.")

    # 3. Read the original data.yaml file
    original_yaml_path = os.path.join(dataset_dir, "data.yaml")
    if not os.path.exists(original_yaml_path):
        raise FileNotFoundError(f"Error: data.yaml config not found at '{original_yaml_path}'")

    with open(original_yaml_path, 'r') as f:
        data_config = yaml.safe_load(f)

    # 4. Inject the dynamically resolved absolute dataset path
    # This ensures it works seamlessly on both local Windows and cloud Linux servers (Render/Vercel)
    data_config['path'] = os.path.abspath(dataset_dir)
    print(f"[INFO] Dynamically resolved dataset path to: {data_config['path']}")

    # 5. Write a temporary yaml configuration inside the backend directory for Ultralytics
    temp_yaml_path = os.path.join(script_dir, "temp_data.yaml")
    with open(temp_yaml_path, 'w') as f:
        yaml.safe_dump(data_config, f)
    print(f"[INFO] Created temporary training config at: {temp_yaml_path}")

    try:
        import torch
        device_to_use = 0 if torch.cuda.is_available() else "cpu"
        print(f"[INFO] PyTorch CUDA check: {'GPU (device=0)' if torch.cuda.is_available() else 'CPU (No CUDA detected)'}")
    except ImportError:
        device_to_use = "cpu"
        print("[WARNING] PyTorch not imported successfully. Defaulting to CPU.")

    try:
        # 6. Dynamically search for the latest checkpoint
        def find_latest_checkpoint(s_dir):
            segment_dir = os.path.join(s_dir, "runs", "segment")
            if not os.path.exists(segment_dir):
                return None
            candidates = []
            for item in os.listdir(segment_dir):
                item_path = os.path.join(segment_dir, item)
                if os.path.isdir(item_path) and (item == "train" or item.startswith("train-") or item.startswith("train")):
                    last_pt = os.path.join(item_path, "weights", "last.pt")
                    if os.path.exists(last_pt):
                        suffix = item.replace("train", "").replace("-", "")
                        try:
                            num = int(suffix) if suffix else 1
                        except ValueError:
                            num = 0
                        candidates.append((num, last_pt))
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                return candidates[0][1]
            return None

        last_checkpoint = find_latest_checkpoint(script_dir)
        
        if last_checkpoint:
            print(f"[INFO] Found latest training checkpoint at: {last_checkpoint}")
            print("[INFO] Resuming training from last epoch...")
            model = YOLO(last_checkpoint)
            
            # 7. Resume training
            model.train(
                data=temp_yaml_path,
                epochs=50,
                imgsz=640,
                batch=4,
                device=device_to_use,
                workers=0,  # Set workers=0 to completely bypass Windows Paging File error (WinError 1455)
                resume=True
            )
        else:
            print("[INFO] No existing checkpoint found. Initializing YOLOv8 Nano Segmentation model...")
            model = YOLO("yolov8n-seg.pt")

            # 7. Start training from scratch
            print(f"[INFO] Starting training pipeline on device: {device_to_use}...")
            model.train(
                data=temp_yaml_path,
                epochs=50,
                imgsz=640,
                batch=4,
                device=device_to_use,
                workers=0  # Set workers=0 to completely bypass Windows Paging File error (WinError 1455)
            )
        print("[SUCCESS] YOLOv8 Segmentation model training complete!")
        print("[SUCCESS] Check the 'runs/segment/train/weights/best.pt' folder for your trained weights.")
        
    finally:
        # 8. Clean up the temporary training config
        if os.path.exists(temp_yaml_path):
            os.remove(temp_yaml_path)
            print("[INFO] Cleaned up temporary training config.")

if __name__ == '__main__':
    main()