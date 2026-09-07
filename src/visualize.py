import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import pickle
import config
import os

# 1. Plot Training History (Accuracy & Loss Graph)
def plot_training_history():
    """
    Training er accuracy, validation accuracy, loss ebong validation loss er graph banabe
    """
    history_path = config.HISTORY_SAVE_PATH
    
    if not os.path.exists(history_path):
        print("❌ Error: Training history file pawa jacche na!")
        print("   Age 'train.py' run kore training complete korun.")
        return
    
    # Load History
    print("⏳ Loading training history...")
    with open(history_path, 'rb') as f:
        history = pickle.load(f)
    
    # Create figure with 2 subplots (Accuracy & Loss)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # --- Plot 1: Accuracy ---
    axes[0].plot(history['accuracy'], label='Training Accuracy', linewidth=2, marker='o')
    axes[0].plot(history['val_accuracy'], label='Validation Accuracy', linewidth=2, marker='s')
    axes[0].set_title('Model Accuracy Over Epochs', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Accuracy', fontsize=12)
    axes[0].legend(loc='lower right')
    axes[0].grid(True, alpha=0.3)
    
    # --- Plot 2: Loss ---
    axes[1].plot(history['loss'], label='Training Loss', linewidth=2, marker='o', color='red')
    axes[1].plot(history['val_loss'], label='Validation Loss', linewidth=2, marker='s', color='orange')
    axes[1].set_title('Model Loss Over Epochs', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Loss', fontsize=12)
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save Image
    save_path = os.path.join(config.LOG_DIR, "training_history.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Training history graph saved at: {save_path}")
    plt.close()

# 2. Plot Confusion Matrix
def plot_confusion_matrix():
    """
    Test data te model er performance er confusion matrix banabe
    """
    print("⏳ Loading Best Model...")
    model = tf.keras.models.load_model(config.MODEL_SAVE_PATH)

    print("📂 Loading Test Data for Confusion Matrix...")
    test_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())
    test_generator = test_datagen.flow_from_directory(
        config.TEST_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    # Predictions
    print("🤖 Predicting on Test Data...")
    Y_pred = model.predict(test_generator)
    y_pred = np.argmax(Y_pred, axis=1)
    y_true = test_generator.classes
    class_names = list(test_generator.class_indices.keys())

    # Generate Matrix
    cm = confusion_matrix(y_true, y_pred)

    # Plotting
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Count'})
    plt.title('Confusion Matrix - Apple Disease Detection', fontsize=16, fontweight='bold')
    plt.ylabel('Actual Class', fontsize=12)
    plt.xlabel('Predicted Class', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save Image
    save_path = os.path.join(config.LOG_DIR, "confusion_matrix.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Confusion Matrix saved at: {save_path}")
    plt.close()

# 3. Plot All Visualizations
def plot_all():
    """
    Sob graph eksathe generate kore
    """
    print("📊 Generating all visualizations...")
    print("\n1️⃣ Training History Graph:")
    plot_training_history()
    
    print("\n2️⃣ Confusion Matrix:")
    plot_confusion_matrix()
    
    print("\n🎉 All visualizations complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "history":
            plot_training_history()
        elif sys.argv[1] == "confusion":
            plot_confusion_matrix()
        elif sys.argv[1] == "all":
            plot_all()
        else:
            print("Usage: python visualize.py [history|confusion|all]")
    else:
        # Default: Show all
        plot_all()