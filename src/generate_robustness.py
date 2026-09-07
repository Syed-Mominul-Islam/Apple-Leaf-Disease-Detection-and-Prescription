import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Paths
base_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT-FINAL-PROJECT\dataset\processed\test"
output_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT_Final_Report\Chap4"
output_file = os.path.join(output_dir, "robustness_sample.png")

# Classes
valid_class = 'Apple_Scab'
invalid_class = 'Not_Apple_Leaf'

# Get images
valid_dir = os.path.join(base_dir, valid_class)
invalid_dir = os.path.join(base_dir, invalid_class)

valid_img_path = os.path.join(valid_dir, os.listdir(valid_dir)[0])
invalid_img_path = os.path.join(invalid_dir, os.listdir(invalid_dir)[0])

# Plot
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# Valid
img1 = mpimg.imread(valid_img_path)
axes[0].imshow(img1)
axes[0].set_title("Valid Input: Apple Scab\n(Prediction: Apple Scab)", fontsize=12, color='green')
axes[0].axis('off')

# Invalid
img2 = mpimg.imread(invalid_img_path)
axes[1].imshow(img2)
axes[1].set_title("Invalid Input: Non-Leaf Object\n(Prediction: Not_Apple_Leaf)", fontsize=12, color='red')
axes[1].axis('off')

plt.tight_layout()
plt.savefig(output_file, dpi=300)
print(f"Robustness figure saved to {output_file}")
