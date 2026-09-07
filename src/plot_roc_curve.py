import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import cycle
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
import config
import os

def plot_roc_curve():
    # 1. Path Settings & Check Model
    model_path = config.MODEL_SAVE_PATH
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}!")
        return

    # Create logs directory if not exists
    os.makedirs(os.path.join(config.BASE_DIR, "logs"), exist_ok=True)

    # 2. Load Model
    print("Loading Best Model...")
    model = tf.keras.models.load_model(model_path)

    # 3. Load Test Data
    print("Loading Test Data for ROC Curve...")
    test_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())
    test_generator = test_datagen.flow_from_directory(
        config.TEST_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    # 4. Predict probabilities
    print("Predicting on Test Data...")
    y_score = model.predict(test_generator)
    y_true = test_generator.classes
    n_classes = config.NUM_CLASSES
    class_names = config.CLASSES

    # Binarize labels for One-vs-Rest ROC calculation
    y_true_bin = label_binarize(y_true, classes=range(n_classes))

    # Calculate ROC and AUC for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Calculate micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    # Calculate macro-average ROC curve and ROC area
    # First aggregate all false positive rates
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

    # Then interpolate all ROC curves at these points
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(n_classes):
        mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])

    # Finally average it and compute AUC
    mean_tpr /= n_classes
    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

    # Plot all ROC curves
    plt.figure(figsize=(10, 8))

    # Plot micro average
    plt.plot(fpr["micro"], tpr["micro"],
             label=f'micro-average ROC (AUC = {roc_auc["micro"]:.2f})',
             color='deeppink', linestyle=':', linewidth=4)

    # Plot macro average
    plt.plot(fpr["macro"], tpr["macro"],
             label=f'macro-average ROC (AUC = {roc_auc["macro"]:.2f})',
             color='navy', linestyle=':', linewidth=4)

    # Colors for different classes
    colors = cycle(['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22'])
    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
                 label=f'ROC of class {class_names[i]} (AUC = {roc_auc[i]:.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=1.5)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (FPR)', fontsize=12)
    plt.ylabel('True Positive Rate (TPR)', fontsize=12)
    plt.title('Multi-class ROC-AUC Curve - Apple Disease Detection', fontsize=14, fontweight='bold', pad=15)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)

    # Save Graph
    save_path = os.path.join(config.LOG_DIR, "roc_curve.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"ROC Curve saved successfully at: {save_path}")
    plt.close()

if __name__ == "__main__":
    plot_roc_curve()
