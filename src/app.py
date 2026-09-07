import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import config
import os
import time

# 1. Page Config (Must be the first command)
st.set_page_config(
    page_title="Apple Doctor AI",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for Professional UI
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Title Styling */
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #28a745;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        height: 55px;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #218838;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Result Box Styling */
    .result-card {
        padding: 25px;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-top: 20px;
        border-left: 5px solid #28a745;
    }
    
    .prescription-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        border: 1px solid #c8e6c9;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Model Loading with Caching
@st.cache_resource
def load_model():
    model_path = config.MODEL_SAVE_PATH
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path)
        except Exception as e:
            st.error(f"❌ Model loading failed: {e}")
            return None
    else:
        st.error("❌ Model file not found! Please check path.")
        return None

# 4. Prescription Database (Enriched)
disease_solutions = {
    "Apple_Scab": {
        "bn_name": "অ্যাপল স্ক্যাব (ছত্রাক)",
        "cause": "Venturia inaequalis ছত্রাকের কারণে হয়।",
        "prescription": "💊 **Prescription:** Captan বা Mancozeb গ্রুপের ছত্রাকনাশক (যেমন: Indofil M-45) ২ গ্রাম/লিটার পানিতে মিশিয়ে স্প্রে করুন। আক্রান্ত পাতা ও ফল সংগ্রহ করে পুড়িয়ে ফেলুন।"
    },
    "Black_Rot": {
        "bn_name": "ব্ল্যাক রট (পচা রোগ)",
        "cause": "Botryosphaeria obtusa ছত্রাকের আক্রমণে হয়।",
        "prescription": "✂️ **Prescription:** গাছের আক্রান্ত ডালপালা কেটে ফেলুন। কাটা অংশে কপার-বেসড (তাম্রযুক্ত) ছত্রাকনাশক পেস্ট লাগান। ফল পেকে যাওয়ার আগে Captan স্প্রে করুন।"
    },
    "Cedar_Apple_Rust": {
        "bn_name": "সিডার অ্যাপল রাস্ট (মরচে রোগ)",
        "cause": "Gymnosporangium juniperi-virginianae ছত্রাক দ্বারা হয়।",
        "prescription": "🌲 **Prescription:** বাগানের আশেপাশে সিডার (Cedar) গাছ থাকলে তা সরিয়ে ফেলুন। জুলাই-আগস্ট মাসে সালফার বা Myclobutanil জাতীয় স্প্রে ব্যবহার করুন।"
    },
    "Alternaria": {
        "bn_name": "অল্টারনারিয়া লিফ ব্লচ",
        "cause": "Alternaria mali ছত্রাকের কারণে হয়।",
        "prescription": "💧 **Prescription:** 'Iprodione' বা 'Mancozeb' গ্রুপের ঔষধ ভালো কাজ করে। ১০-১৫ দিন পর পর স্প্রে করুন। গাছে পানি দেয়ার সময় পাতায় যেন পানি না লাগে।"
    },
    "Apple_Mosaic": {
        "bn_name": "অ্যাপল মোজাইক ভাইরাস",
        "cause": "Apple Mosaic Virus (ApMV) দ্বারা সংক্রমিত হয়।",
        "prescription": "⚠️ **Warning:** এটি একটি ভাইরাসজনিত রোগ। এর কোনো সরাসরি ঔষধ নেই। আক্রান্ত গাছটি দ্রুত মূলসহ তুলে পুড়িয়ে ফেলুন যাতে অন্য গাছে না ছড়ায়।"
    },
    "Healthy": {
        "bn_name": "সুস্থ পাতা (Healthy)",
        "cause": "কোনো রোগ বা পোকার আক্রমণ নেই।",
        "prescription": "✅ **Great!** আপনার গাছটি সম্পূর্ণ সুস্থ আছে। নিয়মিত সঠিক পরিমাণে পানি ও জৈব সার ব্যবহার করুন এবং আগাছা পরিষ্কার রাখুন।"
    },
    "Not_Apple_Leaf": {
        "bn_name": "অগ্রহণযোগ্য ইনপুট (Invalid Input)",
        "cause": "এটি আপেল গাছের পাতা নয়।",
        "prescription": "🚫 **Error:** দয়া করে একটি স্পষ্ট এবং সঠিক আপেল পাতার ছবি আপলোড করুন।"
    }
}

# --- Main App Logic ---

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/415/415733.png", width=120)
    st.markdown("## 🏥 Apple Doctor AI")
    st.write("An advanced AI system for early detection of apple leaf diseases using **AppleNetV1**.")
    st.markdown("---")
    st.info("**Instructions:**\n1. Upload a clear leaf image.\n2. Click 'Analyze Disease'.\n3. Get instant diagnosis & native prescription.")
    st.markdown("---")
    st.caption("Developed for PMIT Final Project")

# Main Content
st.title("🌿 Apple Leaf Disease Detection & Prescription")
st.markdown("### Upload an image to get instant AI-powered analysis.")

# File Uploader
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], help="Supported formats: JPG, PNG, JPEG")

if uploaded_file is not None:
    # Load Model
    model = load_model()

    # Layout: Three Columns for Side-by-Side View
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="medium")

    with col1:
        st.markdown("#### 🖼️ Image")
        image = Image.open(uploaded_file).convert('RGB')
        # Displaying smaller image
        st.image(image, caption="Uploaded Leaf", width=280)
        
        st.markdown("<br>", unsafe_allow_html=True) # Spacing
        analyze_btn = st.button('📋 Analyze Disease')

    # We need to run prediction inside the layout context or before
    
    with col2:
        st.markdown("#### 🔍 Diagnosis")
        # Placeholder or empty space until analysis
        
    if analyze_btn:
        if model is None:
            st.error("Model not ready.")
        else:
            with st.spinner('Processing...'):
                time.sleep(1)

                # Preprocessing
                img_resized = image.resize((config.IMG_WIDTH, config.IMG_HEIGHT))
                img_array = np.array(img_resized).astype(np.float32)
                # Apply model specific preprocessing function
                preprocess_fn = config.get_preprocessing_fn()
                img_array = preprocess_fn(img_array)
                img_array = np.expand_dims(img_array, axis=0)

                # Prediction
                predictions = model.predict(img_array)
                predicted_class_index = np.argmax(predictions)
                confidence_score = np.max(predictions)
                
                # Get Data
                class_key = config.CLASSES[predicted_class_index]
                result_data = disease_solutions.get(class_key, {})
                
                bn_name = result_data.get("bn_name", class_key)
                cause = result_data.get("cause", "N/A")
                prescription = result_data.get("prescription", "No prescription available.")

                # --- Result Display in Col 2 ---
                with col2:
                    color = "#28a745" if class_key == "Healthy" else ("#dc3545" if class_key == "Not_Apple_Leaf" else "#ffc107")
                    
                    st.markdown(f"""
                        <div class="result-card" style="border-left: 5px solid {color}; padding: 15px; margin-top: 0;">
                            <h4 style="color: #666; margin:0;">Result:</h4>
                            <h2 style="color: {color}; margin-top: 5px; font-size: 24px;">{bn_name}</h2>
                            <p style="color: #666; font-size: 14px;">Confidence: <b>{confidence_score * 100:.2f}%</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(int(confidence_score * 100))

                # --- Prescription/Cause in Col 3 ---
                with col3:
                    st.markdown("#### 💊 Prescription & Cause")
                    if class_key != "Not_Apple_Leaf":
                        st.markdown(f"""
                            <div class="prescription-box" style="margin-top: 0;">
                                <p><b>🦠 Cause:</b> {cause}</p>
                                <hr style="margin: 10px 0;">
                                <p style="font-size: 15px;">{prescription}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(prescription)

                    if class_key == "Healthy":
                        st.balloons()

else:
    # Empty State
    st.markdown("""
    <div style="text-align: center; padding: 50px; background-color: white; border-radius: 10px; border: 2px dashed #ccc;">
        <h3 style="color: #7f8c8d;">👈 Awaiting Image Upload</h3>
        <p>Please upload an apple leaf image from the sidebar or drag & drop above.</p>
    </div>
    """, unsafe_allow_html=True)