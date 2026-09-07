import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Paths
base_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT-FINAL-PROJECT\dataset\processed\test"
output_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT_Final_Report\Chap3"
output_file = os.path.join(output_dir, "dataset_samples.png")

# Classes to show (6 types)
classes = ['Alternaria', 'Apple_Mosaic', 'Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy']

# Setup figure
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
axes = axes.flatten()

for i, cls in enumerate(classes):
    cls_dir = os.path.join(base_dir, cls)
    # Get first image
    if os.path.exists(cls_dir):
        files = os.listdir(cls_dir)
        if files:
            img_path = os.path.join(cls_dir, files[0])
            img = mpimg.imread(img_path)
            
            axes[i].imshow(img)
            axes[i].set_title(cls.replace('_', ' '), fontsize=12)
            axes[i].axis('off')
        else:
            axes[i].text(0.5, 0.5, f"No Image\n{cls}", ha='center')
            axes[i].axis('off')
    else:
        axes[i].text(0.5, 0.5, f"Missing Dir\n{cls}", ha='center')
        axes[i].axis('off')

plt.tight_layout()
plt.savefig(output_file, dpi=300)
print(f"Figure saved to {output_file}")
