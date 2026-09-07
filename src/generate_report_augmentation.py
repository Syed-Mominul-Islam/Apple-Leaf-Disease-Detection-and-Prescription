import os
import matplotlib.pyplot as plt
import tensorflow as tf

# Paths
base_dir = r"d:\mahmud-sir\project\dataset\processed\test"
output_dir = r"d:\mahmud-sir\new-report\Chap3"

# Select a sample image
sample_class = 'Apple_Scab'
sample_dir = os.path.join(base_dir, sample_class)

# Check if directory exists
if not os.path.exists(sample_dir):
    print(f"Directory not found: {sample_dir}")
    print("Searching for alternative paths...")
    # Try alternative paths
    alt_paths = [
        r"d:\mahmud-sir\project\dataset\test\Apple_Scab",
        r"d:\mahmud-sir\project\dataset\Apple_Scab",
    ]
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            sample_dir = alt_path
            print(f"Found: {sample_dir}")
            break

sample_img_name = os.listdir(sample_dir)[0]
sample_img_path = os.path.join(sample_dir, sample_img_name)

print(f"Loading image: {sample_img_path}")

# Load image
img = tf.io.read_file(sample_img_path)
img = tf.image.decode_jpeg(img, channels=3)
img = tf.image.resize(img, [224, 224])
img = img / 255.0  # Normalize to [0, 1]

# Create augmentations
def save_single_image(image, filename, title):
    """Save a single image with proper formatting"""
    plt.figure(figsize=(6, 6))
    plt.imshow(image)
    plt.axis('off')
    plt.tight_layout(pad=0)
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Saved: {output_path}")

# 1. Original Image
save_single_image(img, "aug_original.png", "Original")

# 2. Horizontal Flip
flipped = tf.image.flip_left_right(img)
save_single_image(flipped, "aug_horizontal_flip.png", "Horizontal Flip")

# 3. Zoom (Central Crop)
zoomed = tf.image.central_crop(img, central_fraction=0.7)
zoomed = tf.image.resize(zoomed, [224, 224])
save_single_image(zoomed, "aug_zoom.png", "Zoom")

# 4. Rotation (90 degrees)
rotated = tf.image.rot90(img)
save_single_image(rotated, "aug_rotation.png", "Rotation")

# 5. Brightness Variation
bright = tf.image.adjust_brightness(img, delta=0.3)
bright = tf.clip_by_value(bright, 0.0, 1.0)
save_single_image(bright, "aug_brightness.png", "Brightness")

print("\nAll augmentation images generated successfully!")
print(f"Images saved to: {output_dir}")
