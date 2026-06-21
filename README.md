# SCISMO SCAN — Structural Crack Identification & Severity Measurement Online Scanner

An end-to-end framework combining **Deep Learning (YOLOv8 Segmentation)** and **Advanced Digital Image Processing (OpenCV)** to detect concrete cracks, measure width/length, and empirically estimate crack depth. Fully aligned with Indian Standard civil engineering guidelines (**IS 456:2000** and **IS 15988:2013**) for real-time structural health monitoring and automated damage assessment.

---

## 🚀 Quick Start (For Non-Developers)

> **Your friend just needs to follow these 5 steps. No coding knowledge required.**

### Prerequisites (One-Time Install)
1. **Install Python 3.10+** → Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **IMPORTANT**: Check ✅ **"Add Python to PATH"** during installation!
2. **Install Node.js** → Download LTS from [nodejs.org](https://nodejs.org/)
   - Install with default settings (Next → Next → Finish)

### Setup & Run
3. **Download/Extract** this project to any folder
4. **Double-click `SETUP.bat`** — Installs all dependencies automatically (5-10 min, one-time only)
5. **Double-click `START.bat`** — Launches the app and opens your browser 🎉

```
📁 What to click:
    SETUP.bat   → Run ONCE (first time setup)
    START.bat   → Run EVERY TIME to start the app
    STOP.bat    → Stop the app
    TRAIN.bat   → Retrain the YOLO model (optional, needs dataset)
```

> **Note:** The pre-trained YOLO model (`backend/best_structural_model.pt`) must be included when sharing this project. Without it, the app falls back to pure OpenCV processing with reduced accuracy.

---

## 🛠️ System Overview & Architecture

The application adopts a hybrid diagnostic pipeline:
1. **YOLOv8 Deep Learning** segments the core geometry of the crack outlines, ignoring complex shadows, textures, and concrete imperfections.
2. **OpenCV Image Processing** runs a localized sub-millimeter analysis to extract pixel-perfect edges, compute bounding boxes, filter text markings, and calculate physical width, length, and depth.
3. **IS-Code Evaluation Engine** checks the values against nominal concrete cover requirements and returns structural safety classifications and recommended repairs.

---

## 📸 OpenCV Image Processing Pipeline

The system processes incoming specimen photos through a multi-step digital image processing (DIP) pipeline:

### 1. Contrast Limited Adaptive Histogram Equalization (CLAHE)
Grayscale conversions of concrete are enhanced using CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`). This maximizes the local contrast of dark cracks against light gray or weathered concrete surfaces, preventing details from being lost in flat exposures.

### 2. MSER Text Masking
To prevent labels, specimen numbers, or notes written directly on concrete beams/columns from being flagged as cracks, **Maximally Stable Extremal Regions (MSER)** detection is used. The detected text hulls are dilated with a $5 \times 5$ kernel to form a mask that is subtracted from the final threshold map. Text regions that overlap with deep crack voids (global threshold) are preserved to avoid masking true cracks.

### 3. Bilateral Filtering
Traditional Gaussian blurs round out thin cracks. Instead, a Bilateral Filter (`d=9`, `sigmaColor=50`, `sigmaSpace=50`) is applied to smooth high-frequency surface concrete grain noise while preserving the sharp, defined boundaries of true cracks.

### 4. Dual-Path Thresholding (Adaptive + Global)
The system uses two complementary thresholding strategies:
- **Adaptive Gaussian Thresholding** (`blockSize=35`, `C=20`) isolates thin, localized cracks under varying lighting conditions.
- **Global Binary Thresholding** (`threshold=75`) captures wide, deep black voids and gaps that adaptive thresholding may miss.

The system automatically selects the best path based on whether significant wide cracks are detected in the global threshold.

### 5. Contour Extraction & Elongation Filtering
Contours are extracted from the binary map and filtered using structural geometry thresholds:
* **Circularity Constraint**: Circularity ($\mathcal{C}$) must be $< 0.5$ to filter out circular bubble holes or surface voids.
  $$\mathcal{C} = \frac{4\pi \cdot \text{Area}}{\text{Perimeter}^2}$$
* **Aspect Ratio**: Must be $> 1.5$ to ensure the contour is elongated.
* **Area & Perimeter**: Minimum area of $80\text{ px}^2$ and perimeter of $50\text{ px}$ to filter out sensor speckle noise.

> When YOLO pre-validates a region, these thresholds are relaxed (lower min area, perimeter, and aspect ratio) since the ML model has already confirmed crack presence.

---

## 📐 Mathematical Formulations

To measure the physical dimensions of cracks from 2D images, the system performs a coordinate and pixel-to-metric transformation, followed by empirical depth mapping.

### 1. Pixel-to-Millimeter (PPM) Calibration

**Method A — Capture Distance (Default):**
$$\text{PPM} = \frac{W_{\text{pixel}}}{D_{\text{capture}}}$$

**Method B — User-Drawn Calibration Line (Recommended for accuracy):**
$$\text{PPM} = \frac{\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}}{L_{\text{known\_mm}}}$$

Where:
* $W_{\text{pixel}}$ = Total width of the image in pixels.
* $D_{\text{capture}}$ = Capture distance of the camera from the concrete surface in millimeters (default: $300\text{ mm}$).
* $(x_1, y_1), (x_2, y_2)$ = Endpoints of the user-drawn calibration line in pixels.
* $L_{\text{known\_mm}}$ = Known physical length of the calibration reference in millimeters.

### 2. Crack Width and Length Calculation
The contour of a detected crack is enclosed in a minimum-area rotated bounding box ($w_{\text{px}}, h_{\text{px}}$). The physical dimensions are calculated as:

$$\text{Width}_{\text{mm}} = \frac{\min(w_{\text{px}}, h_{\text{px}})}{\text{PPM}}$$

$$\text{Length}_{\text{mm}} = \frac{\max(w_{\text{px}}, h_{\text{px}})}{\text{PPM}}$$

---

### 3. Empirical Depth Estimation (IS 456:2000 Cover Rules)
Since depth cannot be directly measured from a surface photo, the system estimates the crack depth ($d_{\text{mm}}$) relative to the nominal concrete cover requirements of **IS 456:2000** for each structural element:

#### **Column (40 mm Cover)**
$$\text{Depth}_{\text{mm}} = \begin{cases} 
\min(15.0,\, \text{Width}_{\text{mm}} \times 75.0) & \text{if } \text{Width}_{\text{mm}} \le 0.2 \\ 
40.0 & \text{if } 0.2 < \text{Width}_{\text{mm}} \le 0.4 \\ 
\min(40.0 + (\text{Width}_{\text{mm}} - 0.4) \times 80.0,\, 150.0) & \text{if } \text{Width}_{\text{mm}} > 0.4 
\end{cases}$$

#### **Beam (25 mm Cover)**
$$\text{Depth}_{\text{mm}} = \begin{cases} 
\min(10.0,\, \text{Width}_{\text{mm}} \times 50.0) & \text{if } \text{Width}_{\text{mm}} \le 0.2 \\ 
25.0 & \text{if } 0.2 < \text{Width}_{\text{mm}} \le 0.4 \\ 
\min(25.0 + (\text{Width}_{\text{mm}} - 0.4) \times 60.0,\, 100.0) & \text{if } \text{Width}_{\text{mm}} > 0.4 
\end{cases}$$

#### **Slab (20 mm Cover)**
$$\text{Depth}_{\text{mm}} = \begin{cases} 
\min(8.0,\, \text{Width}_{\text{mm}} \times 40.0) & \text{if } \text{Width}_{\text{mm}} \le 0.2 \\ 
20.0 & \text{if } 0.2 < \text{Width}_{\text{mm}} \le 0.4 \\ 
\min(20.0 + (\text{Width}_{\text{mm}} - 0.4) \times 40.0,\, 50.0) & \text{if } \text{Width}_{\text{mm}} > 0.4 
\end{cases}$$

#### **Wall / Pavement (20 mm Cover)**
$$\text{Depth}_{\text{mm}} = \begin{cases} 
\min(8.0,\, \text{Width}_{\text{mm}} \times 40.0) & \text{if } \text{Width}_{\text{mm}} \le 0.2 \\ 
20.0 & \text{if } 0.2 < \text{Width}_{\text{mm}} \le 0.4 \\ 
\min(20.0 + (\text{Width}_{\text{mm}} - 0.4) \times 50.0,\, 60.0) & \text{if } \text{Width}_{\text{mm}} > 0.4 
\end{cases}$$

---

## 🏷️ Roboflow Dataset Configuration

The YOLOv8-segmentation model is trained using a specialized dataset curated and exported via **Roboflow**:
* **Format**: YOLOv8 PyTorch TXT format containing normalized polygon boundary coordinates.
* **Data Splits**: Partitioned into `train/`, `valid/`, and `test/` subdirectories.
* **Class Configuration**: 
  * Class `0`: `crack` (represents the polygon outlines of cracks).
* **Data Annotation**: Fine-grained polygonal masking of crack outlines to capture structural branching, micro-cracking, and structural joints.

---

## 📈 Model Performance & Accuracy Metrics

*Below are the training evaluation metrics compiled from the final YOLOv8-segmentation training output:*

| Metric | Box Detection (Bounding Box) | Mask Detection (Segmentation) |
| :--- | :--- | :--- |
| **Precision (P)** | `0.802` | `0.774` |
| **Recall (R)** | `0.769` | `0.744` |
| **mAP@50** | `0.789` | `0.731` |
| **mAP@50-95** | `0.513` | `0.352` |

### 🖥️ Hardware & Model Performance
* **Model Architecture**: YOLOv8n-seg fused (86 layers, 3,258,259 parameters, 11.3 GFLOPs).
* **Training Platform**: NVIDIA GeForce RTX 3050 A Laptop GPU (4094 MiB).
* **Speed (per image)**:
  * **Pre-process**: `0.5 ms`
  * **Inference**: `4.2 ms`
  * **Post-process**: `2.5 ms`
  * **Total Latency**: `7.2 ms` (equivalent to ~138 FPS raw throughput).

---

## 🩹 Damage Classifications & Repairs (IS 15988:2013)

| Severity | Width Range | Action |
| :--- | :--- | :--- |
| **Low** (Permissible Hairline) | ≤ 0.2 mm | Surface cleaning & elastomeric protective layer application |
| **Medium** (Initial Structural Distress) | 0.2 – 0.4 mm | Low-viscosity structural Epoxy Injection Grouting |
| **High** (Critical Damage) | > 0.4 mm | RCC Jacketing (Columns), CFRP Wrapping (Beams), or Rebar Stitching (Walls) |

---

## 🛠️ Installation & Setup

### Method 1: One-Click Batch Scripts (Recommended)

**Prerequisites**: Install [Python 3.10+](https://www.python.org/downloads/) and [Node.js LTS](https://nodejs.org/).

| Script | Purpose | When to use |
| :--- | :--- | :--- |
| `SETUP.bat` | Creates virtual environment, installs all Python and Node.js dependencies | **Once** (first time only) |
| `START.bat` | Starts backend + frontend servers, opens browser | **Every time** you want to use the app |
| `STOP.bat` | Stops all running servers | When you're done |
| `TRAIN.bat` | Trains/retrains the YOLO model from dataset | Optional (requires `dataset/` folder) |

### Method 2: Manual Setup

#### Backend (FastAPI + Python)
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install PyTorch (CPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# OR Install PyTorch (GPU - NVIDIA CUDA 12.4)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Install remaining dependencies
pip install -r requirements.txt

# Start the backend server
python backend/server.py
```
*Runs API server at `http://127.0.0.1:8000`*

#### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
*Runs frontend interface at `http://localhost:5173`*

#### Model Training (Optional)
```bash
# Requires dataset/ folder with Roboflow-exported data
python backend/train_yolo.py
```
This script auto-detects GPU/CPU, handles Windows memory limitations (`workers=0`), and resumes from the latest checkpoint in `backend/runs/segment/`.

---

## 📁 Project Structure

```
SCISMO_SCAN/
├── SETUP.bat                  # One-time setup script
├── START.bat                  # Start the application
├── STOP.bat                   # Stop all servers
├── TRAIN.bat                  # Train/retrain YOLO model
├── requirements.txt           # Python dependencies
├── .gitignore
├── README.md
│
├── backend/
│   ├── server.py              # FastAPI web server
│   ├── crack_processor.py     # Core detection & measurement pipeline
│   ├── train_yolo.py          # YOLO training script (auto GPU/CPU)
│   ├── best_structural_model.pt  # Pre-trained YOLO model (not in repo*)
│   └── ...                    # Additional utility scripts
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application
│   │   ├── App.css            # Styling
│   │   └── ...
│   ├── package.json
│   └── ...
│
└── dataset/                   # Training dataset (not in repo*)
    ├── data.yaml
    ├── train/
    ├── valid/
    └── test/
```

> **\*** The YOLO model file (`best_structural_model.pt`) and training dataset (`dataset/`) are excluded from the repository due to file size. The model must be shared separately (e.g., via Google Drive or as a GitHub Release asset).

---

## ⚙️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Deep Learning** | YOLOv8n-seg (Ultralytics) |
| **Image Processing** | OpenCV, NumPy, CLAHE, MSER |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend** | React 19 + Vite |
| **Standards** | IS 456:2000, IS 15988:2013 |

---

## 📝 License

This project is developed for academic and research purposes in structural civil engineering.
