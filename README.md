# Civil Crack Assessment & Structural Damage Diagnostics System

An end-to-end framework combining **Deep Learning (YOLOv8 Segmentation)** and **Advanced Digital Image Processing (OpenCV)** to detect concrete cracks, measure width/length, and empirically estimate crack depth. This tool is fully aligned with Indian Standard civil engineering guidelines (**IS 456:2000** and **IS 15988:2013**) to enable real-time structural health monitoring and automated damage assessment.

---

## 🛠️ System Overview & Architecture

The application adopts a hybrid diagnostic pipeline:
1. **YOLOv8 Deep Learning** segments the core geometry of the crack outlines, ignoring complex shadows, textures, and concrete imperfections.
2. **OpenCV Image Processing** runs a localized sub-millimeter analysis to extract pixel-perfect edges, compute bounding boxes, filter text markings, and calculate physical width, length, and depth.
3. **IS-Code Evaluation Engine** checks the values against nominal concrete cover requirements and returns structural safety classifications and recommended repairs.

---

## 📸 OpenCV Image Processing Pipeline

The system processes incoming specimen photos through a multi-step digital image processing (DIP) pipeline:

### 1. Contrast limited Adaptive Histogram Equalization (CLAHE)
Grayscale conversions of concrete are enhanced using CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`). This maximizes the local contrast of dark cracks against light gray or weathered concrete surfaces, preventing details from being lost in flat exposures.

### 2. MSER Text Masking
To prevent labels, specimen numbers, or notes written directly on concrete beams/columns from being flagged as cracks, **Maximally Stable Extremal Regions (MSER)** detection is used. The detected text hulls are dilated with a $5 \times 5$ kernel to form a mask that is subtracted from the final threshold map.

### 3. Bilateral Filtering
Traditional Gaussian blurs round out thin cracks. Instead, a Bilateral Filter (`d=9`, `sigmaColor=50`, `sigmaSpace=50`) is applied to smooth high-frequency surface concrete grain noise while preserving the sharp, defined boundaries of true cracks.

### 4. Adaptive Gaussian Thresholding
Adaptive thresholding (`blockSize=35`, `C=25`) isolates localized dark pixels from surrounding concrete. This allows the system to remain highly robust under varying lighting conditions, uneven shadows, and high-glare indoor/outdoor environments.

### 5. Contour Extraction & Elongation Filtering
Contours are extracted from the binary map and filtered using structural geometry thresholds:
* **Circularity Constraint**: Circularity ($\mathcal{C}$) must be $< 0.5$ to filter out circular bubble holes or surface voids.
  $$\mathcal{C} = \frac{4\pi \cdot \text{Area}}{\text{Perimeter}^2}$$
* **Aspect Ratio**: Must be $> 1.5$ to ensure the contour is elongated.
* **Area & Perimeter**: Minimum area of $40\text{ px}^2$ and perimeter of $30\text{ px}$ to filter out sensor speckle noise.

---

## 📐 Mathematical Formulations

To measure the physical dimensions of cracks from 2D images, the system performs a coordinate and pixel-to-metric transformation, followed by empirical depth mapping.

### 1. Pixel-to-Millimeter (PPM) Calibration
The physical resolution of the image is computed dynamically based on the camera capture distance:
$$\text{PPM} = \frac{W_{\text{pixel}}}{D_{\text{capture}}}$$

Where:
* $W_{\text{pixel}}$ = Total width of the image in pixels.
* $D_{\text{capture}}$ = Capture distance of the camera from the concrete surface in millimeters (default: $300\text{ mm}$).

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

* **Minor / Fine** (Width $< 1.0\text{ mm}$): Cosmetic damage. Recommendations: Surface plastering, sealant coat, painting.
* **Medium** (Width $1.0\text{ mm} - 5.0\text{ mm}$): Moderate structural risk. Recommendations: Non-structural epoxy resin injection.
* **Severe** (Width $> 5.0\text{ mm}$): Immediate structural hazard. Recommendations: Structural pressure grouting, concrete stitching, or localized steel plate jacketing.

---

## 🛠️ Installation & Setup

### 1. Backend Setup (FastAPI)
Requires **Python 3.12**:
1. Activate virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
2. Navigate to backend and run:
   ```powershell
   cd backend
   python server.py
   ```
   *Runs API server at `http://127.0.0.1:8000`.*

### 2. Frontend Setup (React/Vite)
Requires **Node.js**:
1. Navigate to frontend and install dependencies:
   ```powershell
   cd frontend
   npm install
   ```
2. Start the dev server:
   ```powershell
   npm run dev
   ```
   *Runs frontend interface at `http://localhost:5173`.*

### 3. Model Training & Resuming
To train or resume from checkpoint:
```powershell
cd backend
python train_yolo.py
```
This script handles the Windows memory limitations (`workers=0`) and resumes from the latest available checkpoint folder in `backend/runs/segment/`.
