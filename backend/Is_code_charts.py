import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_thesis_plots(csv_path):
    print("--- Starting Academic Chart Visualization Engine ---")
    
    if not os.path.exists(csv_path):
        print(f"Error: Database file '{csv_path}' not found! Run the batch file first.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Configure professional plot style layout
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 11, 'axes.labelsize': 12, 'axes.titlesize': 13})
    
    # =========================================================
    # PLOT 1: CRACK WIDTH FREQUENCY DISTRIBUTION
    # =========================================================
    plt.figure(figsize=(8, 5))
    
    # Filter out non-cracked entries to keep the distribution accurate
    cracked_df = df[df["Calculated Width (mm)"] > 0]
    
    if not cracked_df.empty:
        sns.histplot(data=cracked_df, x="Calculated Width (mm)", kde=True, color="#2980b9", bins=15, linewidth=1.2)
        # Draw explicit Indian Standard Limit Line reference
        plt.axvline(x=0.2, color="red", linestyle="--", linewidth=2, label="IS 456 Limit (0.2 mm)")
        plt.legend(loc="upper right")
    else:
        plt.text(0.5, 0.5, "No Crack Data Available in Dataset", ha='center', va='center')
        
    plt.title("Statistical Distribution of Measured Concrete Crack Widths (SDNET2018)", pad=15, fontweight="bold")
    plt.xlabel("Calculated Real-World Crack Width (mm)")
    plt.ylabel("Frequency / Count of Images")
    plt.tight_layout()
    
    plot1_out = "crack_width_distribution.png"
    plt.savefig(plot1_out, dpi=300)
    print(f"[SUCCESS] Saved dataset histogram chart as: {plot1_out}")
    plt.close()

    # =========================================================
    # PLOT 2: SEISMIC SAFETY TAG BREAKDOWN SUMMARY
    # =========================================================
    plt.figure(figsize=(7, 5))
    
    # Extract structural frequencies
    tag_counts = df["Predicted Seismic Tag"].value_counts()
    
    # Define color scheme corresponding directly to your structural tags
    color_map = {
        "GREEN (Safe)": "#2ecc71", 
        "BLUE (Minor Distress)": "#3498db", 
        "YELLOW (Restricted)": "#f1c40f", 
        "RED (Danger)": "#e74c3c"
    }
    
    # Ensure color indexing matches category density
    plot_colors = [color_map.get(tag, "#7f8c8d") for tag in tag_counts.index]
    
    sns.barplot(x=tag_counts.index, y=tag_counts.values, palette=plot_colors, hue=tag_counts.index, legend=False, edgecolor="black", linewidth=1)
    
    plt.title("Post-Earthquake Seismic Hazard Vulnerability Summary", pad=15, fontweight="bold")
    plt.xlabel("Assigned Structural Safety Evaluation Class")
    plt.ylabel("Number of Processed Concrete Specimens")
    
    # Add exact numeric tally count tags above each column bar
    for i, count_val in enumerate(tag_counts.values):
        plt.text(i, count_val + max(1, int(count_val * 0.01)), str(count_val), ha='center', va='bottom', fontweight='bold', fontsize=10)
        
    plt.tight_layout()
    
    plot2_out = "seismic_safety_summary.png"
    plt.savefig(plot2_out, dpi=300)
    print(f"[SUCCESS] Saved seismic tag summary bar chart as: {plot2_out}")
    plt.close()
    
    print("\n--- All Analytical Graphics Exported Cleanly to Project Directory ---")

if __name__ == "__main__":
    generate_thesis_plots("structural_assessment_report.csv")
