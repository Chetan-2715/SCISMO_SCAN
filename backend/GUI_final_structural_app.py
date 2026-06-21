import os
import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

# Dynamic linkage module connecting Part 1 processing core logic
try:
    from crack_processor import detect_multiple_cracks_end_to_end
except ImportError:
    def detect_multiple_cracks_end_to_end(path, dist):
        return cv2.imread(path), 0, 0.0, 0.0, "Import Failure", "Place crack_processor.py in the same code root path directory folder location.", []

class SeismicDamageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M.Tech Project: Hybrid Seismic Damage Assessment Platform")
        self.root.geometry("1280x720")
        self.root.configure(bg="#243b4a") 
        
        self.current_image_path = None
        self.build_ui_layout()
        
    def build_ui_layout(self):
        header_frame = tk.Frame(self.root, bg="#1a2d3a", height=50)
        header_frame.pack(fill="x", side="top")
        header_title = tk.Label(header_frame, text="AI-Based Predictive Modeling & Post-Seismic Structural Assessment", 
                                 fg="white", bg="#1a2d3a", font=("Helvetica", 14, "bold"), pady=10)
        header_title.pack()

        ctrl_frame = tk.Frame(self.root, bg="#243b4a", pady=15)
        ctrl_frame.pack(fill="x")
        
        tk.Label(ctrl_frame, text="Enter Capture Distance (mm):", fg="white", bg="#243b4a", font=("Helvetica", 10)).pack(side="left", padx=(100, 5))
        self.entry_dist = tk.Entry(ctrl_frame, width=10, justify="center", font=("Helvetica", 10))
        self.entry_dist.insert(0, "300")
        self.entry_dist.pack(side="left", padx=5)
        
        select_btn = tk.Button(ctrl_frame, text="📁 Select Input Frame", bg="#0275d8", fg="white", font=("Helvetica", 10, "bold"),
                               command=self.load_and_process_image_callback, relief="flat", padx=10)
        select_btn.pack(side="left", padx=25)

        main_pane = tk.Frame(self.root, bg="#243b4a")
        main_pane.pack(fill="both", expand=True, padx=20, pady=10)

        left_pane = tk.LabelFrame(main_pane, text="VISUAL INSPECTION STREAM", fg="#5bc0de", bg="#1f323f", font=("Helvetica", 10, "bold"))
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.image_canvas = tk.Label(left_pane, bg="#111c24")
        self.image_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.status_bar = tk.Label(left_pane, text="STATUS: SYSTEM IDLE | AWAITING FRAME PATH", 
                                   fg="#5bc0de", bg="#16252f", font=("Helvetica", 10, "bold"), pady=5)
        self.status_bar.pack(fill="x", side="bottom")

        # --- THIS IS THE RIGHT PANE INTERACTION SPECIFICATION MATRIX ---
        right_pane = tk.LabelFrame(main_pane, text="IS-CODE STRUCTURAL EVALUATION REPORT", fg="#5bc0de", bg="#1f323f", font=("Helvetica", 10, "bold"))
        right_pane.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.lbl_file = tk.Label(right_pane, text="File Name: None", fg="white", bg="#1f323f", anchor="w", font=("Helvetica", 11))
        self.lbl_file.pack(fill="x", padx=15, pady=(20, 5))
        
        self.lbl_total_cracks = tk.Label(right_pane, text="Total Cracks Detected: 0", fg="#ffdd00", bg="#1f323f", anchor="w", font=("Helvetica", 11, "bold"))
        self.lbl_total_cracks.pack(fill="x", padx=15, pady=5)

        self.lbl_width = tk.Label(right_pane, text="Calculated Max Width: 0.00 mm", fg="white", bg="#1f323f", anchor="w", font=("Helvetica", 11))
        self.lbl_width.pack(fill="x", padx=15, pady=5)

        self.lbl_length = tk.Label(right_pane, text="Calculated Total Length: 0.00 mm", fg="white", bg="#1f323f", anchor="w", font=("Helvetica", 11))
        self.lbl_length.pack(fill="x", padx=15, pady=5)

        self.lbl_severity = tk.Label(right_pane, text="IS 456 Severity: None", fg="white", bg="#1f323f", anchor="w", font=("Helvetica", 11))
        self.lbl_severity.pack(fill="x", padx=15, pady=5)
        
        tk.Label(right_pane, text="IS 15988 Repair Workflow Plan:", fg="#d9534f", bg="#1f323f", anchor="w", font=("Helvetica", 11, "bold")).pack(fill="x", padx=15, pady=(15, 2))
        
        self.txt_workflow = tk.Text(right_pane, height=6, bg="#16252f", fg="#ff9999", wrap="word", bd=0, font=("Helvetica", 10, "bold"), padx=5, pady=5)
        self.txt_workflow.pack(fill="x", padx=15, pady=5)
        
        tk.Label(right_pane, text="Segmented Vectors Log Summary Table:", fg="#5bc0de", bg="#1f323f", anchor="w", font=("Helvetica", 10, "bold")).pack(fill="x", padx=15, pady=(10, 2))
        
        self.tree = ttk.Treeview(right_pane, columns=("id", "w", "l"), show="headings", height=6)
        self.tree.heading("id", text="Crack ID")
        self.tree.heading("w", text="Width (mm)")
        self.tree.heading("l", text="Length (mm)")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("w", width=120, anchor="center")
        self.tree.column("l", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_and_process_image_callback(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path:
            return
            
        self.current_image_path = file_path
        
        try:
            distance = int(self.entry_dist.get())
        except ValueError:
            distance = 300
            self.entry_dist.delete(0, tk.END)
            self.entry_dist.insert(0, "300")

        out_frame, total_cnt, max_w, total_l, severity, workflow, logs = detect_multiple_cracks_end_to_end(file_path, distance)
        
        if out_frame is None:
            return
            
        self.lbl_file.config(text=f"File Name: {os.path.basename(file_path)}")
        self.lbl_total_cracks.config(text=f"Total Cracks Detected: {total_cnt}")
        self.lbl_width.config(text=f"Calculated Max Width: {max_w:.2f} mm")
        self.lbl_length.config(text=f"Calculated Total Length: {total_l:.2f} mm")
        self.lbl_severity.config(text=f"IS 456 Severity: {severity}")
        
        self.txt_workflow.delete('1.0', tk.END)
        self.txt_workflow.insert(tk.END, workflow)
        
        if total_cnt == 0:
            self.status_bar.config(text="STATUS: NO DAMAGE DETECTED | STRUCTURE IS COMPLETELY SOUND", fg="#5cb85c")
        elif max_w > 0.4:
            self.status_bar.config(text="STATUS: CRITICAL STRUCTURAL DISTRESS | RISK CODE: HIGH", fg="#d9534f")
        elif max_w > 0.2:
            self.status_bar.config(text="STATUS: INITIAL STRUCTURAL DISTRESS | RISK CODE: MEDIUM", fg="#f0ad4e")
        else:
            self.status_bar.config(text="STATUS: MINOR SURFACE CRACKS | RISK CODE: LOW", fg="#5cb85c")
            
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in logs:
            self.tree.insert("", "end", values=(f"Crack #{row['id']}", f"{row['width']} mm", f"{row['length']} mm"))
            
        rgb_img = cv2.cvtColor(out_frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        
        canvas_w = self.image_canvas.winfo_width()
        canvas_h = self.image_canvas.winfo_height()
        if canvas_w < 50 or canvas_h < 50: 
            canvas_w, canvas_h = 550, 400
            
        pil_img.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        self.image_canvas.config(image=tk_img)
        self.image_canvas.image = tk_img

if __name__ == "__main__":
    root = tk.Tk()
    app = SeismicDamageApp(root)
    root.mainloop()
