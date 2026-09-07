import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import config
import os
import argparse

# 1. Model Load Function
def load_trained_model():
    model_path = config.MODEL_SAVE_PATH
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file pawa jacche na: {model_path}")
        return None
    
    print("⏳ Model load hocche...")
    model = tf.keras.models.load_model(model_path)
    return model

# 2. Prescription Logic
disease_solutions = {
    "Apple_Scab": "💊 Prescription: Captan ba Mancozeb fungicide spray korun. Pata jhore gele soriye felun.",
    "Black_Rot": "💊 Prescription: Infected dal-pala kete felun. Copper-based fungicide spray korun.",
    "Cedar_Apple_Rust": "💊 Prescription: Cedar gach theke dure rakhun. Sulfur spray use korun.",
    "Alternaria": "💊 Prescription: 'Iprodione' ba 'Mancozeb' group er medicine din. Patay pani lagaben na.",
    "Apple_Mosaic": "⚠️ Warning: Virus detected! Infected gach soriye felai valo. Kono medicine nei.",
    "Healthy": "✅ Great! Gach sustho ache. Niyomito pani ebong shaar din.",
    "Not_Apple_Leaf": "🚫 Error: Eta Apple gacher pata noy. Doya kore sothik image din."
}

# 3. Prediction Function
def predict_image_class(model, img_path):
    # Check if image exists
    if not os.path.exists(img_path):
        print(f"❌ Error: Image file pawa jacche na: {img_path}")
        return

    # Image Load & Preprocess
    img = image.load_img(img_path, target_size=(config.IMG_HEIGHT, config.IMG_WIDTH))
    img_array = image.img_to_array(img)
    # Apply model specific preprocessing function
    preprocess_fn = config.get_preprocessing_fn()
    img_array = preprocess_fn(img_array)
    img_array = np.expand_dims(img_array, axis=0) # Batch dimension

    # Prediction
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    confidence = np.max(predictions)

    class_name = config.CLASSES[predicted_class_index]
    solution = disease_solutions.get(class_name, "Solution not found.")

    # Result Print
    print("\n" + "-" * 50)
    print(f"🔍 Analyzing Image...")
    print("-" * 50)
    print(f"🌿 Disease Name : {class_name}")
    print(f"📊 Confidence   : {confidence * 100:.2f}%")
    print(f"📝 {solution}")
    print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apple Leaf Disease Detection")
    parser.add_argument("--image", type=str, help="Path to the leaf image", required=True)
    args = parser.parse_args()

    model = load_trained_model()
    if model:
        predict_image_class(model, args.image)