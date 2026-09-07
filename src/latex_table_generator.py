import pandas as pd
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import config
import numpy as np
import os

def generate_latex_table():
    print("⏳ Loading Best Model...")
    model_path = config.MODEL_SAVE_PATH
    if not os.path.exists(model_path):
        print("❌ Model file not found. Please train first.")
        return

    model = tf.keras.models.load_model(model_path)

    print("📂 Loading Test Data...")
    test_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())
    test_generator = test_datagen.flow_from_directory(
        config.TEST_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    print("🤖 Predicting...")
    Y_pred = model.predict(test_generator)
    y_pred = np.argmax(Y_pred, axis=1)
    y_true = test_generator.classes
    class_names = list(test_generator.class_indices.keys())

    # Get Report Dict
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

    print("\n" + "="*50)
    print("       LATEX TABLE CODE (COPY THIS)       ")
    print("="*50 + "\n")

    print(r"\begin{table}[H]")
    print(r"\centering")
    print(r"\caption{Classification Metrics: Precision, Recall, and F1-Score}")
    print(r"\label{tab:classification_results_summary}")
    print(r"\begin{tabular}{lcccc}")
    print(r"\toprule")
    print(r"\textbf{Class} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} & \textbf{Support} \\")
    print(r"\midrule")

    # Rows
    for class_name in class_names:
        precision = report[class_name]['precision']
        recall = report[class_name]['recall']
        f1 = report[class_name]['f1-score']
        support = report[class_name]['support']
        
        # Format class name (replace underscores with spaces for LaTeX textual display if needed, 
        # but keep Not_Apple_Leaf with underscore escaped)
        display_name = class_name
        if "Not" in display_name:
             display_name = r"Not\_Apple\_Leaf"
        else:
             display_name = display_name.replace("_", " ")

        print(f"{display_name} & {precision:.2f} & {recall:.2f} & {f1:.2f} & {support} \\\\")

    print(r"\midrule")
    
    # Average Row
    wa = report['weighted avg']
    print(r"\textbf{Weighted Average} & \textbf{" + f"{wa['precision']:.2f}" + r"} & \textbf{" + f"{wa['recall']:.2f}" + r"} & \textbf{" + f"{wa['f1-score']:.2f}" + r"} & \textbf{" + f"{wa['support']}" + r"} \\\\")
    
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")
    print("\n" + "="*50)

if __name__ == "__main__":
    generate_latex_table()
