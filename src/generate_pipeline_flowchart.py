import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import config

# 1. Paths and Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "dataset", "processed")
TEST_DIR = os.path.join(DATA_DIR, "test")
MODEL_PATH = os.path.join(BASE_DIR, "models", "appleNetV1", "appleNetV1_model.keras")
ARTIFACT_DIR = r"C:\Users\Tizaraa\.gemini\antigravity-ide\brain\d40a4bd7-4a34-43c5-a428-84d41757f435"

# Find a sample image
sample_img_path = None
classes = config.CLASSES
for c in classes:
    class_dir = os.path.join(TEST_DIR, c)
    if os.path.exists(class_dir):
        files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            sample_img_path = os.path.join(class_dir, files[0])
            sample_class = c
            break

if not sample_img_path:
    raise FileNotFoundError("Could not find any sample image in test dataset.")

print(f"Using sample image: {sample_img_path} (Class: {sample_class})")

# Load and preprocess sample image
img_raw = Image.open(sample_img_path).convert('RGB')
img_resized = img_raw.resize((224, 224))
img_arr = np.array(img_resized).astype(np.float32) / 255.0
img_batch = np.expand_dims(img_arr, axis=0)

# Load Model
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")

# Predictions
preds = model.predict(img_batch)
pred_class_idx = np.argmax(preds[0])
pred_class_name = classes[pred_class_idx]
pred_confidence = preds[0][pred_class_idx]

# 2. Grad-CAM Implementation
def get_gradcam(img_array, model, last_conv_layer_name):
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = inputs
    layer_outputs = {}
    for layer in model.layers:
        x = layer(x)
        layer_outputs[layer.name] = x
    
    grad_model = tf.keras.models.Model(
        inputs=inputs, 
        outputs=[layer_outputs[last_conv_layer_name], x]
    )
    
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, np.argmax(predictions[0])]
    
    output = conv_outputs[0]
    grads = tape.gradient(loss, conv_outputs)[0]
    
    gate_f = tf.cast(output > 0, "float32")
    gate_g = tf.cast(grads > 0, "float32")
    guided_grads = gate_f * gate_g * grads
    
    weights = tf.reduce_mean(guided_grads, axis=(0, 1))
    cam = np.zeros(output.shape[0:2], dtype=np.float32)
    
    for i, w in enumerate(weights):
        cam += w * output[:, :, i]
        
    cam = np.maximum(cam, 0)
    if np.max(cam) > 0:
        cam = cam / np.max(cam)
    
    cam_img = Image.fromarray(np.uint8(cam * 255)).resize((224, 224), Image.Resampling.LANCZOS)
    return np.array(cam_img) / 255.0

# 2.1. Grad-CAM++ Implementation
def get_gradcam_plusplus(img_array, model, last_conv_layer_name):
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = inputs
    layer_outputs = {}
    for layer in model.layers:
        x = layer(x)
        layer_outputs[layer.name] = x
    
    grad_model = tf.keras.models.Model(
        inputs=inputs, 
        outputs=[layer_outputs[last_conv_layer_name], x]
    )
    
    with tf.GradientTape() as tape_3:
        with tf.GradientTape() as tape_2:
            with tf.GradientTape() as tape_1:
                conv_outputs, predictions = grad_model(img_array)
                class_idx = np.argmax(predictions[0])
                loss = predictions[:, class_idx]
            grads_1 = tape_1.gradient(loss, conv_outputs)
        grads_2 = tape_2.gradient(grads_1, conv_outputs)
    grads_3 = tape_3.gradient(grads_2, conv_outputs)
    
    output = conv_outputs[0]
    grads_val = grads_1[0]
    grads_2_val = grads_2[0]
    grads_3_val = grads_3[0]
    
    spatial_sum = tf.reduce_sum(output * grads_3_val, axis=(0, 1), keepdims=True)
    denominator = 2.0 * grads_2_val + spatial_sum
    denominator = tf.where(denominator != 0.0, denominator, tf.ones_like(denominator))
    alpha = grads_2_val / denominator
    
    weights = tf.reduce_sum(alpha * tf.maximum(grads_val, 0.0), axis=(0, 1))
    
    cam = np.zeros(output.shape[0:2], dtype=np.float32)
    for i, w in enumerate(weights.numpy()):
        cam += w * output[:, :, i].numpy()
        
    cam = np.maximum(cam, 0)
    if np.max(cam) > 0:
        cam = cam / np.max(cam)
        
    cam_img = Image.fromarray(np.uint8(cam * 255)).resize((224, 224), Image.Resampling.LANCZOS)
    return np.array(cam_img) / 255.0

print("Generating Grad-CAM heatmap...")
heatmap = get_gradcam(img_batch, model, "conv2d_3")

# 3. Create Augmentations
def get_augmentations(image):
    img_tensor = tf.convert_to_tensor(image)
    aug1 = tf.image.flip_left_right(img_tensor).numpy()
    aug2 = tf.image.rot90(img_tensor, k=1).numpy()
    aug3 = tf.image.central_crop(img_tensor, 0.7)
    aug3 = tf.image.resize(aug3, [224, 224]).numpy()
    aug4 = tf.image.adjust_brightness(img_tensor, 0.25).numpy()
    aug4 = np.clip(aug4, 0.0, 1.0)
    return [aug1, aug2, aug3, aug4]

aug_imgs = get_augmentations(img_arr)
aug_labels = ["Horizontal Flip", "90° Rotation", "Center Crop (Zoom)", "Brightness (+0.25)"]

# 4. Draw Flowchart
fig = plt.figure(figsize=(18, 12), facecolor='#f8f9fa')
ax_bg = fig.add_axes([0, 0, 1, 1], facecolor='none')
ax_bg.axis('off')
ax_bg.set_xlim(0, 1)
ax_bg.set_ylim(0, 1)

# Style configuration
c_accent = '#3b82f6'
c_border = '#cbd5e1'

def draw_card(ax, title, title_y=0.9, bg_color='#ffffff', border_color='#cbd5e1'):
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    rect = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.01", linewidth=1.5, edgecolor=border_color, facecolor=bg_color, zorder=0)
    ax.add_patch(rect)
    ax.text(0.5, title_y, title, ha='center', va='center', fontsize=12, fontweight='bold', color='#1e293b', zorder=5)

def draw_global_arrow(start_x, start_y, end_x, end_y, text=""):
    ax_bg.annotate(text, xy=(end_x, end_y), xytext=(start_x, start_y),
                   arrowprops=dict(facecolor='#475569', edgecolor='#475569', shrink=0.05, width=1.5, headwidth=6, headlength=6),
                   ha='center', va='center', fontsize=9, color='#475569', fontweight='bold')

# Gridspec Layout
# Row 1: Data Acquisition (col 0), Preprocessing (col 1), Augmentation (col 2-3)
# Row 2: CNN Architecture (span 4 cols)
# Row 3: Output Classification (col 0), XAI (col 1-3)
gs = fig.add_gridspec(3, 4, height_ratios=[1.2, 1.8, 1.4], hspace=0.35, wspace=0.3)

# --- ROW 1, COL 0: DATA ACQUISITION ---
ax1 = fig.add_subplot(gs[0, 0])
draw_card(ax1, "1. Data Acquisition")
ax1.imshow(img_raw, extent=[0.08, 0.48, 0.15, 0.72], zorder=1)
ax1.set_aspect('auto')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.text(0.52, 0.43, f"Source: Dataset\nClass: {sample_class.replace('_', ' ')}\nSize: {img_raw.size[0]}x{img_raw.size[1]}x3", 
         ha='left', va='center', fontsize=8.5, color='#475569', fontweight='bold', linespacing=1.4, zorder=5)

# --- ROW 1, COL 1: PREPROCESSING ---
ax2 = fig.add_subplot(gs[0, 1])
draw_card(ax2, "2. Preprocessing")
# Draw a neat input/output representation box inside Preprocessing
rect_box = patches.FancyBboxPatch((0.15, 0.15), 0.7, 0.6, boxstyle="round,pad=0.01", linewidth=1, edgecolor='#cbd5e1', facecolor='#f8fafc', zorder=1)
ax2.add_patch(rect_box)
ax2.text(0.5, 0.45, "Image Resizing\n224 x 224\n\nPixel Normalization\n[0, 1] range (/255.0)", 
         ha='center', va='center', fontsize=9.5, color='#334155', fontweight='bold', linespacing=1.4, zorder=5)

# --- ROW 1, COL 2-3: DATA AUGMENTATION ---
ax3 = fig.add_subplot(gs[0, 2:])
draw_card(ax3, "3. Data Augmentation (ImageDataGenerator)")
for i in range(4):
    ax3.imshow(aug_imgs[i], extent=[0.05 + i*0.235, 0.05 + i*0.235 + 0.19, 0.15, 0.70], zorder=1)
    ax3.text(0.05 + i*0.235 + 0.095, 0.77, aug_labels[i], ha='center', va='center', fontsize=8, color='#334155', fontweight='bold', zorder=5)
ax3.set_aspect('auto')
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)

# --- ROW 2: APPLENETV1 CORE CNN ARCHITECTURE ---
ax_arch = fig.add_subplot(gs[1, :])
draw_card(ax_arch, "AppleNetV1 Deep Convolutional Neural Network (Core Architecture)", title_y=0.92, bg_color='#f1f5f9', border_color='#94a3b8')

# Draw layers as blocks
layer_names = [
    "Input Layer\n224x224x3",
    "Conv Block 1\nConv2D (32, 3x3)\nBatchNorm + ReLU\nMaxPool (2x2)",
    "Conv Block 2\nConv2D (64, 3x3)\nBatchNorm + ReLU\nMaxPool (2x2)",
    "Conv Block 3\nConv2D (128, 3x3)\nBatchNorm + ReLU\nMaxPool (2x2)",
    "Conv Block 4\nConv2D (256, 3x3)\nBatchNorm + ReLU\nMaxPool (2x2)",
    "Dense Block\nFlatten\nDense (512)\nBatchNorm + ReLU\nDropout (0.5)",
    "Classifier\nDense (7)\nSoftmax"
]

shapes = [
    "(224, 224, 3)",
    "(112, 112, 32)",
    "(56, 56, 64)",
    "(28, 28, 128)",
    "(14, 14, 256)",
    "(50176) -> (512)",
    "(7)"
]

block_colors = ['#3b82f6', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4']

for i in range(7):
    bx = 0.035 + i * 0.135
    by = 0.12
    bw = 0.115
    bh = 0.68
    
    # Background card for block
    rect = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.01", linewidth=1, edgecolor='#cbd5e1', facecolor='#ffffff', zorder=1)
    ax_arch.add_patch(rect)
    
    # Header color block
    header_rect = patches.FancyBboxPatch((bx, by + bh - 0.12), bw, 0.12, boxstyle="round,pad=0.01", linewidth=0, facecolor=block_colors[i], zorder=2)
    ax_arch.add_patch(header_rect)
    
    title_text = layer_names[i].split('\n')[0]
    ax_arch.text(bx + bw/2, by + bh - 0.06, title_text, ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff', zorder=3)
    
    body_text = "\n".join(layer_names[i].split('\n')[1:])
    ax_arch.text(bx + bw/2, by + bh - 0.2, body_text, ha='center', va='top', fontsize=8, color='#334155', linespacing=1.2, zorder=3)
    
    ax_arch.text(bx + bw/2, by + 0.06, f"Shape:\n{shapes[i]}", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=block_colors[i], zorder=3)
    
    if i < 6:
        ax_arch.annotate("", xy=(bx + bw + 0.018, by + bh/2), xytext=(bx + bw, by + bh/2),
                         arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', shrink=0.05, width=1.2, headwidth=4.5, headlength=4.5), zorder=4)

# --- ROW 3, COL 0: CLASSIFICATION RESULT ---
ax_res = fig.add_subplot(gs[2, 0])
draw_card(ax_res, "5. Classification Output")

# Display top predictions in bar-style indicators inside the card
top_indices = np.argsort(preds[0])[::-1][:3]
for rank, idx in enumerate(top_indices):
    prob = preds[0][idx]
    class_name = classes[idx].replace('_', ' ')
    
    ry = 0.52 - rank * 0.2
    # Progress bar outline
    rect_outline = patches.FancyBboxPatch((0.1, ry), 0.8, 0.06, boxstyle="round,pad=0.01", edgecolor='#cbd5e1', facecolor='#e2e8f0', zorder=1)
    ax_res.add_patch(rect_outline)
    
    # Progress bar filled
    if prob > 0:
        rect_fill = patches.FancyBboxPatch((0.1, ry), 0.8 * prob, 0.06, boxstyle="round,pad=0.01", edgecolor='#22c55e', facecolor='#22c55e', zorder=2)
        ax_res.add_patch(rect_fill)
        
    ax_res.text(0.1, ry + 0.1, f"{class_name}", ha='left', va='center', fontsize=9, fontweight='bold', color='#1e293b', zorder=5)
    ax_res.text(0.9, ry + 0.1, f"{prob*100:.1f}%", ha='right', va='center', fontsize=9, fontweight='bold', color='#1e293b', zorder=5)

# --- ROW 3, COL 1-3: EXPLAINABLE AI (XAI) ---
ax_xai = fig.add_subplot(gs[2, 1:])
draw_card(ax_xai, "6. Explainable AI (XAI) using Grad-CAM at layer: conv2d_3", bg_color='#feffec', border_color='#fef08a')

# Display XAI image triad
ax_xai.imshow(img_arr, extent=[0.08, 0.31, 0.12, 0.70], zorder=1)
ax_xai.text(0.195, 0.76, "Original Image", ha='center', va='center', fontsize=9, fontweight='bold', color='#475569', zorder=5)

ax_xai.imshow(heatmap, cmap='jet', extent=[0.385, 0.615, 0.12, 0.70], zorder=1)
ax_xai.text(0.50, 0.76, "Grad-CAM Heatmap", ha='center', va='center', fontsize=9, fontweight='bold', color='#475569', zorder=5)

ax_xai.imshow(img_arr, extent=[0.69, 0.92, 0.12, 0.70], zorder=1)
ax_xai.imshow(heatmap, cmap='jet', alpha=0.45, extent=[0.69, 0.92, 0.12, 0.70], zorder=2)
ax_xai.text(0.805, 0.76, "Superimposed Explanation", ha='center', va='center', fontsize=9, fontweight='bold', color='#475569', zorder=5)

# Highlighting overlay focus label
ax_xai.text(0.805, 0.16, "Lesion Spot Activated", ha='center', va='center', fontsize=7.5, color='#ffffff', fontweight='bold', 
            bbox=dict(facecolor='#ef4444', alpha=0.8, pad=3, lw=0, boxstyle="round"), zorder=5)

ax_xai.set_aspect('auto')
ax_xai.set_xlim(0, 1)
ax_xai.set_ylim(0, 1)

# --- GLOBAL ARROWS AND CONNECTIONS ---
# Card 1 -> Card 2
draw_global_arrow(0.245, 0.82, 0.275, 0.82)
# Card 2 -> Card 3
draw_global_arrow(0.485, 0.82, 0.515, 0.82)
# Card 3 -> Arch input
draw_global_arrow(0.73, 0.72, 0.11, 0.62, "Feed Preprocessed Image")
# Arch output -> Result & XAI
draw_global_arrow(0.89, 0.40, 0.21, 0.31, "Predict")
draw_global_arrow(0.91, 0.40, 0.61, 0.31, "Explain")

# --- OVERALL PIPELINE TITLE ---
fig.suptitle("Apple Leaf Disease Diagnosis Pipeline using AppleNetV1", fontsize=22, fontweight='bold', color='#1e293b', y=0.97)

# --- SAVE ---
# Save in workspace
workspace_save_path = os.path.join(BASE_DIR, "AppleNetV1_Pipeline_Flowchart.png")
plt.savefig(workspace_save_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
print(f"Flowchart saved to workspace at: {workspace_save_path}")

# Save in artifact directory
artifact_save_path = os.path.join(ARTIFACT_DIR, "AppleNetV1_Pipeline_Flowchart.png")
os.makedirs(ARTIFACT_DIR, exist_ok=True)
plt.savefig(artifact_save_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
print(f"Flowchart saved to artifact dir at: {artifact_save_path}")

plt.close()
