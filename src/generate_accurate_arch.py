import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_arch_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    color_input = '#3498db'   # Blue
    color_conv = '#e67e22'    # Orange
    color_pool = '#e74c3c'    # Red
    color_dense = '#2ecc71'   # Green
    color_output = '#9b59b6'  # Purple

    def draw_box(x, y, w, h, label, color, subtext=""):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", linewidth=2, edgecolor='#2c3e50', facecolor=color)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2 + 1, label, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        if subtext:
            ax.text(x + w/2, y + h/2 - 2.5, subtext, ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    def draw_arrow(x, y, dx, dy):
        ax.arrow(x, y, dx, dy, head_width=1.5, head_length=2, fc='#2c3e50', ec='#2c3e50', length_includes_head=True)

    # 1. Input Layer
    draw_box(10, 40, 15, 20, "Input Image", color_input, "224x224x3")
    draw_arrow(25, 50, 5, 0)

    # 2. Conv Block 1
    draw_box(30, 40, 15, 20, "Conv Block 1", color_conv, "32 Filters (3x3)")
    draw_arrow(45, 50, 5, 0)

    # 3. Conv Block 2
    draw_box(50, 40, 15, 20, "Conv Block 2", color_conv, "64 Filters (3x3)")
    draw_arrow(65, 50, 5, 0)

    # 4. Conv Block 3
    draw_box(70, 40, 15, 20, "Conv Block 3", color_conv, "128 Filters (3x3)")
    draw_arrow(85, 50, 5, 0)

    # --- Vertical Break for layout ---
    draw_arrow(92.5, 40, 0, -10)

    # 5. Conv Block 4 (Moving down)
    draw_box(70, 10, 15, 20, "Conv Block 4", color_conv, "256 Filters (3x3)")
    draw_arrow(70, 20, -10, 0)

    # 6. Flatten & Dense
    draw_box(50, 10, 15, 20, "Flatten & Dense", color_dense, "512 Units")
    draw_arrow(50, 20, -10, 0)

    # 7. Output Layer
    draw_box(30, 10, 15, 20, "Output Layer", color_output, "6 Classes (Softmax)")

    plt.title("AppleNetV1: Custom 4-Block CNN Architecture", fontsize=16, fontweight='bold', pad=20)
    
    # Save Path
    save_path = r'd:\mahmud-sir\new-report\Chap3\ccn_architecture_diagram.png'
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    print(f"Diagram saved to: {save_path}")

if __name__ == "__main__":
    create_arch_diagram()
