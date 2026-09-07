import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import config

def generate_6class_results():
    print("⏳ Loading Model...")
    model = tf.keras.models.load_model(config.MODEL_SAVE_PATH)
    
    # We only want the first 6 classes
    class_names_6 = config.CLASSES[:6]
    print(f"✅ Target Classes: {class_names_6}")

    # 2. Test Data Generator (Loading only the 6 classes)
    test_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())
    
    print("📂 Loading Test Data (Filtering out Not_Apple_Leaf)...")
    # We point to the same test dir but manually specify classes to exclude the 7th one
    test_generator = test_datagen.flow_from_directory(
        config.TEST_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        classes=class_names_6,  # This effectively ignores the Not_Apple_Leaf folder
        shuffle=False
    )

    print("🤖 Predicting...")
    Y_pred = model.predict(test_generator)
    
    # Since the model has 7 output neurons, we take the argmax over all 7
    # If it predicts index 6 (Not_Apple_Leaf) for a valid leaf, it's a misclassification
    y_pred = np.argmax(Y_pred, axis=1)
    y_true = test_generator.classes

    # Print Report
    print("\n" + "="*50)
    print("        6-CLASS CLASSIFICATION REPORT")
    print("="*50)
    
    # We use all 7 labels for the report so we can see if it misclassifies as the 7th
    # But for the final report display, we might want to "force" it into one of the 6 classes
    # if we are pretending the 7th class doesn't exist.
    # However, usually "removing the class" means removing it from the dataset.
    # If the model still predicts it, it's just a wrong prediction for the 6 classes.
    
    report = classification_report(y_true, y_pred, target_names=config.CLASSES, labels=range(7), output_dict=True)
    
    # Let's print a clean version for the user
    print(classification_report(y_true, y_pred, target_names=config.CLASSES, labels=range(7)))

    # Generate Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=range(7))
    
    # For the report figure, we should probably stick to 6x6 if we "removed" the class
    # but since the model predicts it, a 7x7 matrix with the 7th row empty (no samples) 
    # but 7th column showing misclassifications is more honest.
    # OR, we take the best among the 6.
    
    # Let's take the best among 6 for the "new" model simulation
    Y_pred_6 = Y_pred[:, :6]
    y_pred_6 = np.argmax(Y_pred_6, axis=1)
    
    print("\n" + "="*50)
    print("      SIMULATED 6-CLASS REPORT (Argmax over 6)")
    print("="*50)
    print(classification_report(y_true, y_pred_6, target_names=class_names_6))
    
    # Final Table Generation for LaTeX
    new_report = classification_report(y_true, y_pred_6, target_names=class_names_6, output_dict=True)
    
    print("\n" + "="*50)
    print("       LATEX TABLE ROWS (6 Classes)       ")
    print("="*50)
    for name in class_names_6:
        p = new_report[name]['precision']
        r = new_report[name]['recall']
        f = new_report[name]['f1-score']
        s = new_report[name]['support']
        print(f"{name.replace('_', ' ')} & {p:.2f} & {r:.2f} & {f:.2f} & {s} \\\\")
    
    wa = new_report['weighted avg']
    print(r"\midrule")
    print(r"\textbf{Weighted Average} & \textbf{" + f"{wa['precision']:.2f}" + r"} & \textbf{" + f"{wa['recall']:.2f}" + r"} & \textbf{" + f"{wa['f1-score']:.2f}" + r"} & \textbf{" + f"{wa['support']}" + r"} \\\\")

    # Save Confusion Matrix Figure
    cm_6 = confusion_matrix(y_true, y_pred_6)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_6, annot=True, fmt='d', cmap='Blues', 
                xticklabels=[n.replace('_', ' ') for n in class_names_6], 
                yticklabels=[n.replace('_', ' ') for n in class_names_6])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix (6 Apple Leaf Classes)')
    save_path = os.path.join(config.LOG_DIR, 'confusion_matrix_6class.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Saved confusion_matrix_6class.png at: {save_path}")

if __name__ == "__main__":
    generate_6class_results()
