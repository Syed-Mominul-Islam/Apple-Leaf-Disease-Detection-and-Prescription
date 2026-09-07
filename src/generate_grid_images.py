import os
from PIL import Image, ImageDraw, ImageFont

# Define paths
base_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\source-code"
images_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\images"
raw_data_dir = os.path.join(base_dir, "dataset", "Raw_Data")
gradcam_dir = os.path.join(base_dir, "logs", "appleNetV1", "gradcam")
web_dir = os.path.join(images_dir, "web")

os.makedirs(images_dir, exist_ok=True)

# Font settings for labeling
try:
    font = ImageFont.truetype("arial.ttf", 20)
    font_large = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()
    font_large = ImageFont.load_default()

def make_dataset_samples():
    print("Generating dataset_samples.png...")
    classes = ['Alternaria', 'Apple_Mosaic', 'Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy', 'Not_Apple_Leaf']
    
    # We will create a 2x4 grid of raw dataset images
    # Each image cell: 250x250, with a 30px label bar at the bottom. Cell total: 250x280.
    cell_w, cell_h = 250, 250
    label_h = 35
    grid_cols = 4
    grid_rows = 2
    
    grid_img = Image.new("RGB", (cell_w * grid_cols + 50, (cell_h + label_h) * grid_rows + 40), (255, 255, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for idx, c in enumerate(classes):
        c_dir = os.path.join(raw_data_dir, c)
        if not os.path.exists(c_dir):
            print(f"Directory not found: {c_dir}")
            continue
        files = [f for f in os.listdir(c_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            continue
        
        # Load first image
        img_path = os.path.join(c_dir, files[0])
        cell_img = Image.open(img_path).convert("RGB")
        cell_img = cell_img.resize((cell_w, cell_h))
        
        # Calculate position
        row = idx // grid_cols
        col = idx % grid_cols
        x = col * (cell_w + 10) + 15
        y = row * (cell_h + label_h + 10) + 15
        
        # Paste image
        grid_img.paste(cell_img, (x, y))
        
        # Draw border
        draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(200, 200, 200), width=2)
        
        # Draw label
        display_name = c.replace("_", " ")
        # Center text
        text_bbox = draw.textbbox((0, 0), display_name, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = x + (cell_w - text_w) // 2
        text_y = y + cell_h + 5
        draw.text((text_x, text_y), display_name, fill=(0, 0, 0), font=font)
        
    save_path = os.path.join(images_dir, "dataset_samples.png")
    grid_img.save(save_path)
    print(f"Saved dataset samples grid to {save_path}")

def make_gradcam_grid():
    print("Generating gradcam_grid.png...")
    files = [
        "Alternaria_gradcam.png",
        "Apple_Scab_gradcam.png",
        "Black_Rot_gradcam.png",
        "Cedar_Apple_Rust_gradcam.png"
    ]
    
    # Each raw image has size 4440x1533.
    # We will resize each to 1110x383.
    # We will lay them out in a 2x2 grid. Total size: 2220x766.
    cell_w, cell_h = 1110, 383
    grid_cols = 2
    grid_rows = 2
    
    grid_img = Image.new("RGB", (cell_w * grid_cols + 20, cell_h * grid_rows + 20), (255, 255, 255))
    
    for idx, fname in enumerate(files):
        fpath = os.path.join(gradcam_dir, fname)
        if not os.path.exists(fpath):
            print(f"Gradcam file not found: {fpath}")
            continue
        cell_img = Image.open(fpath).convert("RGB")
        cell_img = cell_img.resize((cell_w, cell_h))
        
        row = idx // grid_cols
        col = idx % grid_cols
        x = col * (cell_w + 5) + 5
        y = row * (cell_h + 5) + 5
        
        grid_img.paste(cell_img, (x, y))
        
    save_path = os.path.join(images_dir, "gradcam_grid.png")
    grid_img.save(save_path)
    print(f"Saved Grad-CAM grid to {save_path}")

def make_web_app_screenshots():
    print("Generating web_app_screenshots.png...")
    # List of files in images/web
    files = [
        ("alternatia.png", "Alternaria"),
        ("mosaic.png", "Apple Mosaic"),
        ("scab.png", "Apple Scab"),
        ("black-rot.png", "Black Rot"),
        ("cedar-rust.png", "Cedar Apple Rust"),
        ("healthy.png", "Healthy"),
        ("Not-apple-leaf.png", "Not Apple Leaf")
    ]
    
    # 2x4 grid of Streamlit app screenshots.
    # Each cell: 350x262 (approx 4:3), cell container 350x292 with label
    cell_w, cell_h = 350, 262
    label_h = 30
    grid_cols = 4
    grid_rows = 2
    
    grid_img = Image.new("RGB", (cell_w * grid_cols + 30, (cell_h + label_h) * grid_rows + 20), (255, 255, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for idx, (fname, label) in enumerate(files):
        fpath = os.path.join(web_dir, fname)
        if not os.path.exists(fpath):
            print(f"Web screenshot not found: {fpath}")
            continue
        cell_img = Image.open(fpath).convert("RGB")
        cell_img = cell_img.resize((cell_w, cell_h))
        
        row = idx // grid_cols
        col = idx % grid_cols
        x = col * (cell_w + 5) + 10
        y = row * (cell_h + label_h + 5) + 10
        
        grid_img.paste(cell_img, (x, y))
        
        # Border
        draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(220, 220, 220), width=1)
        
        # Label
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = x + (cell_w - text_w) // 2
        text_y = y + cell_h + 3
        draw.text((text_x, text_y), label, fill=(50, 50, 50), font=font)
        
    save_path = os.path.join(images_dir, "web_app_screenshots.png")
    grid_img.save(save_path)
    print(f"Saved Web App screenshots grid to {save_path}")

if __name__ == "__main__":
    make_dataset_samples()
    make_gradcam_grid()
    make_web_app_screenshots()
