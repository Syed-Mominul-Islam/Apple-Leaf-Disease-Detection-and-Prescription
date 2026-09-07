import os

# Base Paths
# Amra dhore nicchi code ta 'src' folder theke run hobe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "dataset", "processed")

TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "val")
TEST_DIR = os.path.join(DATA_DIR, "test")

# Model selection: "appleNetV1", "mobilenetv2", "resnet50", "densenet121", "efficientnetb0"
MODEL_NAME = "appleNetV1"

# Dynamic outputs
MODEL_DIR = os.path.join(BASE_DIR, "models", MODEL_NAME)
LOG_DIR = os.path.join(BASE_DIR, "logs", MODEL_NAME)

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

MODEL_SAVE_PATH = os.path.join(MODEL_DIR, f"{MODEL_NAME}_model.keras")
HISTORY_SAVE_PATH = os.path.join(LOG_DIR, f"{MODEL_NAME}_history.pkl")

# Hyperparameters (Training Settings)
IMG_HEIGHT = 224
IMG_WIDTH = 224
CHANNELS = 3          # RGB
BATCH_SIZE = 32       # Ekbare koyta image process korbe
EPOCHS = 25           # Kotobar puro dataset dekhbe
LEARNING_RATE = 0.001

# Class Names (Serial ta folder er nam onujayi hote hobe)
CLASSES = ['Alternaria', 'Apple_Mosaic', 'Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy', 'Not_Apple_Leaf']
NUM_CLASSES = len(CLASSES)

def get_preprocessing_fn():
    """
    Model onujayi preprocessing function return kore
    """
    if MODEL_NAME == "mobilenetv2":
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        return preprocess_input
    elif MODEL_NAME == "resnet50":
        from tensorflow.keras.applications.resnet50 import preprocess_input
        return preprocess_input
    elif MODEL_NAME == "densenet121":
        from tensorflow.keras.applications.densenet import preprocess_input
        return preprocess_input
    elif MODEL_NAME == "efficientnetb0":
        from tensorflow.keras.applications.efficientnet import preprocess_input
        return preprocess_input
    elif MODEL_NAME == "vgg16":
        from tensorflow.keras.applications.vgg16 import preprocess_input
        return preprocess_input
    elif MODEL_NAME == "vgg19":
        from tensorflow.keras.applications.vgg19 import preprocess_input
        return preprocess_input
    else:
        # appleNetV1 scale standard [0, 1] e kore
        return lambda x: x / 255.0