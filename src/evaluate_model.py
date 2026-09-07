import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import config
import os
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

def evaluate():
    # 1. Model Load
    print("⏳ Loading Best Model...")
    model_path = config.MODEL_SAVE_PATH
    if not os.path.exists(model_path):
        print("❌ Model file pawa jacche na.")
        return
    
    model = tf.keras.models.load_model(model_path)

    # 2. Test Data Generator
    # Test data te kono augmentation hobe na, shudhu preprocess
    test_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())

    print("📂 Loading Test Data...")
    test_generator = test_datagen.flow_from_directory(
        config.TEST_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False  # Shuffle bondho rakhben confusion matrix er jonno
    )

    # 3. Evaluate (Loss & Accuracy)
    print("🚀 Starting Evaluation...")
    loss, accuracy = model.evaluate(test_generator)
    print("-" * 50)
    print(f"🏆 Final Test Accuracy: {accuracy * 100:.2f}%")
    print(f"📉 Final Test Loss: {loss:.4f}")
    print("-" * 50)

    # 4. Detailed Report (Confusion Matrix & F1-Score)
    # Eta apnar Project Report/Viva-r jonno khub dorkar
    print("📊 Generating Detailed Report...")
    
    Y_pred = model.predict(test_generator)
    y_pred = np.argmax(Y_pred, axis=1) # Predicted Class
    y_true = test_generator.classes    # Actual Class

    # Class Names
    class_labels = list(test_generator.class_indices.keys())

    # Print Report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=class_labels))

if __name__ == "__main__":
    evaluate()