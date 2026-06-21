import { useState, useRef } from 'react';
import { 
  Upload, 
  Settings, 
  Activity, 
  FileText, 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle,
  HelpCircle,
  Eye,
  Info,
  Maximize2
} from 'lucide-react';

// Custom SVG Chart Components
function CrackWidthHistogram({ cracks }) {
  if (!cracks || cracks.length === 0) {
    return (
      <div className="viewer-placeholder" style={{ height: '150px' }}>
        <Info size={24} />
        <span>No crack metrics available for statistical plotting.</span>
      </div>
    );
  }
  
  const widths = cracks.map(c => c.width);
  const maxVal = Math.max(...widths, 1.2);
  const numBins = 8;
  const binWidth = maxVal / numBins;
  const bins = Array(numBins).fill(0);
  
  cracks.forEach(c => {
    let idx = Math.floor(c.width / binWidth);
    if (idx >= numBins) idx = numBins - 1;
    bins[idx]++;
  });
  
  const maxCount = Math.max(...bins, 1);
  
  // SVG Setup
  const width = 300;
  const height = 150;
  const padding = 25;
  const chartW = width - padding * 2;
  const chartH = height - padding * 2;
  
  return (
    <div className="chart-container">
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* Horizontal grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
          const y = padding + chartH * (1 - ratio);
          return (
            <line
              key={i}
              x1={padding}
              y1={y}
              x2={width - padding}
              y2={y}
              className="chart-grid-line"
            />
          );
        })}
        
        {/* Histogram Bars */}
        {bins.map((count, i) => {
          const barW = chartW / numBins - 3;
          const barH = (count / maxCount) * chartH;
          const x = padding + i * (chartW / numBins) + 1.5;
          const y = padding + chartH - barH;
          return (
            <rect
              key={i}
              x={x}
              y={y}
              width={barW}
              height={barH}
              fill="#5bc0de"
              rx="2"
              opacity="0.85"
            />
          );
        })}
        
        {/* Axes */}
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} className="chart-axis" />
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="chart-axis" />
        
        {/* IS 456 Permissible Limit Line (0.2 mm) */}
        {(() => {
          const limitPos = 0.2;
          if (limitPos <= maxVal) {
            const x = padding + (limitPos / maxVal) * chartW;
            return (
              <g>
                <line
                  x1={x}
                  y1={padding}
                  x2={x}
                  y2={height - padding}
                  className="chart-limit-line"
                />
                <text x={x + 3} y={padding + 12} fill="#ef4444" fontSize="7px" fontWeight="bold" fontFamily="Outfit">
                  IS 456 Limit (0.2mm)
                </text>
              </g>
            );
          }
        })()}
        
        {/* X Axis Labels */}
        <text x={padding} y={height - padding + 10} className="chart-text" textAnchor="middle">0</text>
        <text x={padding + chartW / 2} y={height - padding + 10} className="chart-text" textAnchor="middle">{(maxVal / 2).toFixed(2)}</text>
        <text x={width - padding} y={height - padding + 10} className="chart-text" textAnchor="middle">{maxVal.toFixed(2)} mm</text>
        
        {/* Y Axis Label */}
        <text x={10} y={height / 2} className="chart-text" transform={`rotate(-90 10 ${height / 2})`} textAnchor="middle">Count</text>
      </svg>
    </div>
  );
}

function SafetyTagSummary({ cracks }) {
  if (!cracks || cracks.length === 0) return null;
  
  // Count counts of safety classes based on width
  // Safe: <= 0.2mm, Restricted: 0.2 - 1.0mm, Critical: > 1.0mm
  let safe = 0;
  let restricted = 0;
  let danger = 0;
  
  cracks.forEach(c => {
    if (c.width <= 0.2) safe++;
    else if (c.width <= 1.0) restricted++;
    else danger++;
  });
  
  const categories = [
    { label: "Safe (<=0.2mm)", count: safe, color: "#22c55e" },
    { label: "Restricted (0.2-1mm)", count: restricted, color: "#eab308" },
    { label: "Danger (>1.0mm)", count: danger, color: "#ef4444" }
  ];
  
  const maxCount = Math.max(safe, restricted, danger, 1);
  
  const width = 300;
  const height = 110;
  const padding = 20;
  const barMaxW = width - 110; // reserve space for text
  
  return (
    <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {categories.map((cat, i) => {
        const barW = (cat.count / maxCount) * barMaxW;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem' }}>
            <span style={{ width: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
              {cat.label}
            </span>
            <div style={{ flex: 1, height: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '6px', overflow: 'hidden' }}>
              <div 
                style={{ 
                  width: `${(cat.count / maxCount) * 100}%`, 
                  height: '100%', 
                  background: cat.color, 
                  borderRadius: '6px',
                  transition: 'width 0.5s ease' 
                }} 
              />
            </div>
            <span style={{ width: '20px', fontWeight: 'bold', textAlign: 'right', color: cat.color }}>
              {cat.count}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function App() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [distance, setDistance] = useState("300");
  const [elementType, setElementType] = useState("Auto");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("annotated");
  const [dragActive, setDragActive] = useState(false);
  
  // Scale Calibration States
  const [drawing, setDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const [showScaleDialog, setShowScaleDialog] = useState(false);
  const [scaleLength, setScaleLength] = useState("40");
  const [isCalibrated, setIsCalibrated] = useState(false);
  
  const fileInputRef = useRef(null);
  
  // Drag and Drop triggers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("image/")) {
        setImageFile(file);
        setImagePreview(URL.createObjectURL(file));
        setResult(null);
        setError(null);
        setStartPoint(null);
        setEndPoint(null);
        setIsCalibrated(false);
        setShowScaleDialog(false);
      } else {
        setError("Invalid file type. Please upload a valid image (PNG/JPG).");
      }
    }
  };
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setStartPoint(null);
      setEndPoint(null);
      setIsCalibrated(false);
      setShowScaleDialog(false);
    }
  };
  
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };
  
  const handleMouseDown = (e) => {
    if (activeTab !== 'original') return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    setDrawing(true);
    setStartPoint({ x, y });
    setEndPoint({ x, y });
    setIsCalibrated(false);
  };

  const handleMouseMove = (e) => {
    if (!drawing) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    setEndPoint({ x, y });
  };

  const handleMouseUp = () => {
    if (!drawing) return;
    setDrawing(false);
    setShowScaleDialog(true);
  };

  const handleClearCalibration = () => {
    setStartPoint(null);
    setEndPoint(null);
    setIsCalibrated(false);
    setShowScaleDialog(false);
  };

  const handleProcessImage = async () => {
    if (!imageFile) return;
    
    setIsLoading(true);
    setError(null);
    
    const parsedDistance = Math.max(10, parseInt(distance) || 300);
    
    const formData = new FormData();
    formData.append("file", imageFile);
    formData.append("element_type", elementType);

    if (isCalibrated && startPoint && endPoint) {
      const lineStr = `${startPoint.x},${startPoint.y},${endPoint.x},${endPoint.y}`;
      formData.append("calibration_line", lineStr);
      formData.append("calibration_length_mm", parseFloat(scaleLength) || 40.0);
    } else {
      formData.append("capture_distance_mm", parsedDistance);
    }
    
    try {
      const response = await fetch("http://127.0.0.1:8000/api/process", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process the concrete image.");
      }
      
      const data = await response.json();
      if (data.success) {
        setResult(data);
        setActiveTab("annotated");
      } else {
        throw new Error("API responded with failure status.");
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "An unexpected error occurred during model inference.");
    } finally {
      setIsLoading(false);
    }
  };
  
  // Dynamic color selection based on severity status
  const getSeverityInfo = (sevStr) => {
    const s = String(sevStr).toLowerCase();
    if (s.includes("high") || s.includes("critical") || s.includes("severe")) {
      return {
        className: "severity-high",
        icon: <ShieldAlert size={16} />,
        label: "CRITICAL DANGER",
        text: "Exceeds all durability limits. High collapsing risk under seismic activity. Conforms to RCC/FRP wrapper specifications (IS 15988:2013 Cl 8.4)."
      };
    } else if (s.includes("medium") || s.includes("moderate") || s.includes("distress")) {
      return {
        className: "severity-medium",
        icon: <AlertTriangle size={16} />,
        label: "MODERATE DISTRESS",
        text: "Exceeds standard durability thresholds. Structural injection and resin packing required (IS 15988:2013 Cl 8.2)."
      };
    } else {
      return {
        className: "severity-low",
        icon: <CheckCircle size={16} />,
        label: "SAFE / HAIRLINE",
        text: "Permissible cracking widths. Cosmetic surface coating and weathering treatments recommended (IS 15988:2013 Cl 8.1 / IS 456 Cl 35.3.2)."
      };
    }
  };
  
  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="header">
        <div className="header-title-group">
          <h1 style={{ 
            fontSize: '2rem', 
            background: 'linear-gradient(135deg, #5bc0de 0%, #0275d8 100%)', 
            WebkitBackgroundClip: 'text', 
            WebkitTextFillColor: 'transparent', 
            fontWeight: '800',
            letterSpacing: '-0.5px',
            margin: 0
          }}>
            SeismoScan
          </h1>
          <p style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)', margin: '0.15rem 0 0 0' }}>
            Post-Seismic Structural Assessment & Crack Diagnostics
          </p>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.15rem 0 0 0' }}>
            B.Tech Civil Engineering Project Integration Platform — IS 456:2000 & IS 15988:2013
          </p>
        </div>
        <div className="header-badge">
          <Activity size={14} />
          <span>ALGORITHM STREAM ONLINE</span>
        </div>
      </header>
      
      <main className="dashboard-main">
        {/* Left Control Sidebar */}
        <aside className="sidebar">
          {/* Card 1: Camera Calibration & Member type */}
          <div className="panel-card">
            <h3 className="panel-title">
              <Settings size={16} />
              <span>Diagnostic Setup</span>
            </h3>
            
            <div className="form-group">
              <label className="form-label">Member Type Selection</label>
              <select 
                className="form-select"
                value={elementType}
                onChange={(e) => setElementType(e.target.value)}
              >
                <option value="Auto">Auto-Detect via YOLO</option>
                <option value="Beam">Beam (25mm cover)</option>
                <option value="Column">Column (40mm cover)</option>
                <option value="Slab">Slab (20mm cover)</option>
                <option value="Wall/Pavement">Wall / Pavement / Deck</option>
              </select>
            </div>
            
            <div className="form-group" style={{ opacity: isCalibrated ? 0.4 : 1, transition: 'opacity 0.2s' }}>
              <label className="form-label">
                Capture Distance (mm) {isCalibrated && <span style={{ color: '#ff00ff', fontSize: '0.65rem' }}>(Overridden by Ruler)</span>}
              </label>
              <input 
                type="number" 
                className="form-input" 
                min="10" 
                max="5000" 
                value={distance} 
                disabled={isCalibrated}
                onChange={(e) => setDistance(e.target.value)}
                onBlur={() => setDistance(prev => String(Math.max(10, parseInt(prev) || 300)))}
              />
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                {isCalibrated ? "Calibrated with dynamic ruler line." : "Enter distance between camera and surface in millimeters."}
              </span>
            </div>
            
            {isCalibrated && (
              <div style={{
                background: 'rgba(255,0,255,0.08)',
                border: '1px solid rgba(255,0,255,0.2)',
                borderRadius: '6px',
                padding: '0.5rem',
                fontSize: '0.72rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                color: '#f482ff',
                marginBottom: '1rem'
              }}>
                <span>Scale: {scaleLength}mm dynamic calibration line active</span>
                <button 
                  onClick={handleClearCalibration}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#ef4444',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    padding: '2px 6px'
                  }}
                >
                  Clear Scale
                </button>
              </div>
            )}
          </div>
          
          {/* Card 2: Image Selection */}
          <div className="panel-card">
            <h3 className="panel-title">
              <Upload size={16} />
              <span>Specimen Loading</span>
            </h3>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              style={{ display: 'none' }}
              accept="image/*"
            />
            
            <div 
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
            >
              <Upload className="upload-icon" size={28} />
              <div className="upload-text">
                <h4>Drag & Drop File</h4>
                <p>or click to browse local files</p>
              </div>
            </div>
            
            {imageFile && (
              <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '200px' }}>
                  Selected: {imageFile.name}
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {(imageFile.size / 1024).toFixed(0)} KB
                </span>
              </div>
            )}
            
            <button 
              className="btn-primary" 
              style={{ marginTop: '1rem' }}
              onClick={handleProcessImage}
              disabled={!imageFile || isLoading}
            >
              {isLoading ? (
                <>
                  <svg className="spinner" width="16" height="16" viewBox="0 0 50 50">
                    <circle className="path" cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle>
                  </svg>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Maximize2 size={16} />
                  <span>Run IS-Code Diagnostics</span>
                </>
              )}
            </button>
          </div>
          
          {/* Diagnostic Charts */}
          {result && (
            <div className="panel-card">
              <h3 className="panel-title">
                <FileText size={16} />
                <span>Diagnostics Charts</span>
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                    Width Distribution Histogram
                  </span>
                  <CrackWidthHistogram cracks={result.crack_logs} />
                </div>
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                    Distress Class Summary
                  </span>
                  <SafetyTagSummary cracks={result.crack_logs} />
                </div>
              </div>
            </div>
          )}
        </aside>
        
        {/* Right Dashboard Area */}
        <section className="content-pane">
          {/* Column 1: Visual Inspection stream */}
          <div className="panel-card visual-viewer">
            <h3 className="panel-title">
              <Eye size={16} />
              <span>Visual Inspection Stream</span>
            </h3>
            
            <div className="tab-bar">
              <button 
                className={`tab-btn ${activeTab === 'original' ? 'active' : ''}`}
                onClick={() => setActiveTab('original')}
                disabled={!imagePreview}
              >
                Original Frame
              </button>
              <button 
                className={`tab-btn ${activeTab === 'annotated' ? 'active' : ''}`}
                onClick={() => setActiveTab('annotated')}
                disabled={!result}
              >
                Annotated Overlay
              </button>
              <button 
                className={`tab-btn ${activeTab === 'mask' ? 'active' : ''}`}
                onClick={() => setActiveTab('mask')}
                disabled={!result}
              >
                Segmentation Mask
              </button>
            </div>
            
            <div className="image-canvas-wrapper" style={{ position: 'relative' }}>
              {!imagePreview && (
                <div className="viewer-placeholder">
                  <Upload size={32} />
                  <span>Upload a concrete specimen photo to initiate scan</span>
                </div>
              )}
              {imagePreview && activeTab === 'original' && (
                <div 
                  style={{ 
                    position: 'relative', 
                    width: '100%', 
                    height: '100%', 
                    cursor: 'crosshair', 
                    userSelect: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                >
                  <img src={imagePreview} className="canvas-image" alt="Original Specimen" draggable="false" />
                  
                  {/* Calibration Line Overlay */}
                  {startPoint && endPoint && (
                    <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                      <line 
                        x1={`${startPoint.x * 100}%`} 
                        y1={`${startPoint.y * 100}%`} 
                        x2={`${endPoint.x * 100}%`} 
                        y2={`${endPoint.y * 100}%`} 
                        stroke="#ff00ff" 
                        strokeWidth="3" 
                      />
                      <circle cx={`${startPoint.x * 100}%`} cy={`${startPoint.y * 100}%`} r="5" fill="#ff00ff" />
                      <circle cx={`${endPoint.x * 100}%`} cy={`${endPoint.y * 100}%`} r="5" fill="#ff00ff" />
                      {isCalibrated && (
                        <text 
                          x={`${(startPoint.x + endPoint.x) / 2 * 100}%`} 
                          y={`${(Math.min(startPoint.y, endPoint.y) * 100) - 2}%`} 
                          fill="#ff00ff" 
                          fontSize="11px" 
                          fontWeight="bold" 
                          textAnchor="middle"
                          style={{ paintOrder: 'stroke fill', stroke: '#090e12', strokeWidth: '3px' }}
                        >
                          {scaleLength}mm scale
                        </text>
                      )}
                    </svg>
                  )}
                </div>
              )}
              {result && activeTab === 'annotated' && (
                <img src={result.visual_assets.annotated_b64} className="canvas-image" alt="Annotated Specimen" />
              )}
              {result && activeTab === 'mask' && (
                <img src={result.visual_assets.mask_b64} className="canvas-image" alt="Binary Mask" />
              )}

              {/* Floating Ruler Calibration Dialogue */}
              {showScaleDialog && (
                <div style={{
                  position: 'absolute',
                  bottom: '12px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'rgba(12, 20, 26, 0.95)',
                  border: '1px solid rgba(91, 192, 222, 0.2)',
                  padding: '0.4rem 0.8rem',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  zIndex: 20,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.6)'
                }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>Ruler Length:</span>
                  <input 
                    type="number" 
                    value={scaleLength}
                    onChange={(e) => setScaleLength(e.target.value)}
                    style={{
                      width: '55px',
                      padding: '0.2rem 0.4rem',
                      background: '#090e12',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '4px',
                      color: 'white',
                      fontSize: '0.75rem',
                      textAlign: 'center'
                    }}
                  />
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>mm</span>
                  <button 
                    onClick={() => {
                      setIsCalibrated(true);
                      setShowScaleDialog(false);
                    }}
                    style={{
                      background: '#0275d8',
                      color: 'white',
                      border: 'none',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.72rem',
                      fontWeight: 'bold',
                      cursor: 'pointer'
                    }}
                  >
                    Save
                  </button>
                  <button 
                    onClick={handleClearCalibration}
                    style={{
                      background: 'transparent',
                      color: '#ef4444',
                      border: 'none',
                      fontSize: '0.72rem',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
            
            {error && (
              <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#fca5a5', padding: '0.75rem', borderRadius: '8px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldAlert size={16} />
                <span>Error: {error}</span>
              </div>
            )}
          </div>
          
          {/* Column 2: Engineering Report */}
          <div className="panel-card" style={{ display: 'flex', flexString: 1, flexDirection: 'column', gap: '1rem', overflow: 'hidden' }}>
            <h3 className="panel-title">
              <FileText size={16} />
              <span>IS-Code Assessment Report</span>
            </h3>
            
            {result ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto', flex: 1, paddingRight: '0.2rem' }}>
                {/* 1. Safety Alerts */}
                {(() => {
                  const severityDetails = getSeverityInfo(result.severity);
                  return (
                    <div className={`code-alert ${severityDetails.className}`}>
                      <div className="code-alert-title">
                        {severityDetails.icon}
                        <span>{severityDetails.label} — {result.severity}</span>
                      </div>
                      <div className="code-alert-body">
                        {severityDetails.text}
                      </div>
                    </div>
                  );
                })()}
                
                {/* 2. Numeric Metrics */}
                <div className="metrics-grid">
                  <div className="metric-badge">
                    <span className="metric-badge-label">Cracks Found</span>
                    <span className="metric-badge-value">{result.total_cracks}</span>
                  </div>
                  <div className="metric-badge">
                    <span className="metric-badge-label">Max Width</span>
                    <span className="metric-badge-value">{result.max_width_mm.toFixed(2)} mm</span>
                  </div>
                  <div className="metric-badge">
                    <span className="metric-badge-label">Total Length</span>
                    <span className="metric-badge-value">{result.total_length_mm.toFixed(2)} mm</span>
                  </div>
                  <div className="metric-badge">
                    <span className="metric-badge-label">Estimated Depth</span>
                    <span className="metric-badge-value" style={{ color: '#ff8888' }}>
                      {result.max_depth_mm > 0 ? `${result.max_depth_mm.toFixed(2)} mm` : "N/A"}
                    </span>
                  </div>
                </div>
                
                {/* 3. IS 15988 Repair Workflow Plan */}
                <div>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 'bold', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                    IS 15988 Remediation Plan:
                  </h4>
                  <div className="workflow-box">
                    {result.workflow}
                  </div>
                </div>
                
                {/* 4. Crack Log Table */}
                <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: '150px' }}>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 'bold', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                    Segmented Vector Log Summary:
                  </h4>
                  <div className="logs-table-container">
                    <table className="logs-table">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Width</th>
                          <th>Length</th>
                          <th>Estimated Depth</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.crack_logs.map((log) => (
                          <tr key={log.id}>
                            <td style={{ fontWeight: 'bold', color: '#5bc0de' }}>Crack #{log.id}</td>
                            <td>{log.width.toFixed(2)} mm</td>
                            <td>{log.length.toFixed(2)} mm</td>
                            <td style={{ color: '#ffaaaa', fontWeight: '600' }}>{log.depth.toFixed(2)} mm</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="viewer-placeholder" style={{ flex: 1, justifyContent: 'center' }}>
                <FileText size={36} />
                <span>Upload and analyze an image to view structural calculations</span>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
