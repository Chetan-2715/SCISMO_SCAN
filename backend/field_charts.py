import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_field_inspection_results(csv_path):
    print("--- Generating Visual Analytics for Smartphone Field Test ---")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found! Run the batch file first.")
        return
        
    df = pd.read_csv(csv_path)
    sns.set_theme(style="whitegrid")
    
    # =========================================================
    # CHART 1: COMPARATIVE CRACK DIMENSIONS BY FILE (BAR CHART)
    # =========================================================
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=df, x="Site Image File", y="Measured Width (mm)", hue="Predicted Seismic Tag", palette={"YELLOW (Restricted)": "#f0ad4e", "RED (Danger)": "#d9534f"}, edgecolor="black")
    
    # Draw Indian Standard Limit line reference
    plt.axvline = plt.axhline(y=0.2, color="blue", linestyle="--", linewidth=1.5, label="IS 456 Permissible Limit (0.2 mm)")
    
    plt.title("Calculated Smartphone Crack Width vs. Structural Safety Thresholds", pad=15, fontweight='bold')
    plt.xlabel("Evaluated Real-Field Site Image Specimens")
    plt.ylabel("Computed Crack Width Dimension (mm)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    
    chart_out1 = "field_crack_comparison.png"
    plt.savefig(chart_out1, dpi=300)
    print(f"[SUCCESS] Saved field metric comparison chart: {chart_out1}")
    plt.close()

if __name__ == "__main__":
    plot_field_inspection_results("real_field_assessment_report.csv")
