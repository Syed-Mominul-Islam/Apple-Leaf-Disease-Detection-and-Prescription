import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tensorflow as tf
import numpy as np

# Paths
base_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT-FINAL-PROJECT\dataset\processed\test"
output_dir = r"d:\PMIT-FINAL-REPORT-WRITING\PMIT_Final_Report\Chap3"
output_file = os.path.join(output_dir, "augmentation_samples.png")

# Select a sample image
sample_class = 'Apple_Scab'
sample_dir = os.path.join(base_dir, sample_class)
sample_img_name = os.listdir(sample_dir)[0]
sample_img_path = os.path.join(sample_dir, sample_img_name)

# Load image
img = tf.io.read_file(sample_img_path)
img = tf.image.decode_jpeg(img, channels=3)
img = tf.image.resize(img, [224, 224])
img = img / 255.0  # Normalize to [0, 1]

# Create augmentations
def apply_augmentations(image):
    original = image
    
    # 1. Flip Left-Right
    flipped = tf.image.flip_left_right(image)
    
    # 2. Rotation (90 degrees)
    rotated = tf.image.rot90(image)
    
    # 3. Brightness
    bright = tf.image.adjust_brightness(image, delta=0.2)
    bright = tf.clip_by_value(bright, 0.0, 1.0)
    
    # 4. Zoom (Crop and Resize)
    # Central crop of 80% and resize back
    zoomed = tf.image.central_crop(image, central_fraction=0.7)
    zoomed = tf.image.resize(zoomed, [224, 224])
    
    return original, flipped, rotated, bright, zoomed

original, flipped, rotated, bright, zoomed = apply_augmentations(img)

# Plot
fig, axes = plt.subplots(1, 5, figsize=(15, 4))
titles = ['Original', 'Horizontal Flip', 'Rotation (90°)', 'Brightness +', 'Zoom (Crop)']
images = [original, flipped, rotated, bright, zoomed]

for i, ax in enumerate(axes):
    ax.imshow(images[i])
    ax.set_title(titles[i], fontsize=12)
    ax.axis('off')

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Augmentation figure saved to {output_file}")
