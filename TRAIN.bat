@echo off
title SCISMO SCAN - Model Training
color 0E
echo.
echo  ============================================================
echo       SCISMO SCAN - YOLO Model Training
echo  ============================================================
echo.
echo  REQUIREMENTS:
echo    - Dataset folder must be present at: dataset\
echo    - Download dataset from: [Your dataset source]
echo    - GPU recommended (NVIDIA with CUDA) but CPU works too
echo.

if not exist "venv\Scripts\python.exe" (
    color 0C
    echo  ERROR: Run SETUP.bat first!
    pause
    exit /b 1
)

if not exist "dataset" (
    color 0C
    echo  ERROR: Dataset folder not found!
    echo  Please download and place the dataset in the "dataset" folder.
    echo.
    pause
    exit /b 1
)

echo  Starting training... (this may take several hours)
echo  You can close this window to stop training at any time.
echo  Training will resume from the last checkpoint next time.
echo.

call venv\Scripts\python.exe backend\train_yolo.py

echo.
echo  ============================================================
echo  Training complete! 
echo  Copy the trained model:
echo    FROM: backend\runs\segment\train\weights\best.pt
echo    TO:   backend\best_structural_model.pt
echo  ============================================================
echo.
pause
