import os
import sys
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image

# Setup paths
base_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\source-code"
src_path = os.path.join(base_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

import config

# Paths
MODEL_PATH = os.path.join(base_dir, "models", "appleNetV1", "appleNetV1_model.keras")
TEST_DIR = os.path.join(base_dir, "dataset", "processed", "test")
GRADCAM_DIR = os.path.join(base_dir, "logs", "appleNetV1", "gradcam")

# Import functions from pipeline flowchart
from generate_pipeline_flowchart import get_gradcam_plusplus

def main():
    print("Loading model for Grad-CAM++ image generation...")
    model = tf.keras.models.load_model(MODEL_PATH)
    
    classes = ['Alternaria', 'Apple_Mosaic', 'Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy', 'Not_Apple_Leaf']
    
    for c in classes:
        class_dir = os.path.join(TEST_DIR, c)
        if not os.path.exists(class_dir):
            print(f"Directory not found: {class_dir}")
            continue
        files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            continue
        
        # Load sample image
        img_path = os.path.join(class_dir, files[0])
        img_raw = Image.open(img_path).convert('RGB')
        img_resized = img_raw.resize((224, 224))
        img_arr = np.array(img_resized).astype(np.float32) / 255.0
        img_batch = np.expand_dims(img_arr, axis=0)
        
        # Generate Grad-CAM++ heatmap
        heatmap = get_gradcam_plusplus(img_batch, model, "conv2d_3")
        
        # Create visual representation: Original, Heatmap, Overlay (Like standard Grad-CAM style)
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        
        axes[0].imshow(img_arr)
        axes[0].set_title("Original Image")
        axes[0].axis('off')
        
        axes[1].imshow(heatmap, cmap='jet')
        axes[1].set_title("Grad-CAM++ Heatmap")
        axes[1].axis('off')
        
        axes[2].imshow(img_arr)
        axes[2].imshow(heatmap, cmap='jet', alpha=0.45)
        axes[2].set_title("Grad-CAM++ Overlay")
        axes[2].axis('off')
        
        plt.tight_layout()
        save_path = os.path.join(GRADCAM_DIR, f"{c}_gradcam_plusplus.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated and saved: {save_path}")

if __name__ == "__main__":
    main()
