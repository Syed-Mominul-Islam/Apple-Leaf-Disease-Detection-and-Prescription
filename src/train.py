import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import config
import model as model_builder # Amader model.py file
import os

def train():
    # 1. Image Data Generators (Augmentation & Loading)
    print("⏳ Data Generators Setup hocche...")

    # Training Data (Ektu ghuriye pechiye dibe jate model valo shekhe)
    train_datagen = ImageDataGenerator(
        preprocessing_function=config.get_preprocessing_fn(),
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Validation Data (Eta sudhu preprocess hobe, no augmentation)
    val_datagen = ImageDataGenerator(preprocessing_function=config.get_preprocessing_fn())

    # Load Data from Folders
    train_generator = train_datagen.flow_from_directory(
        config.TRAIN_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )

    val_generator = val_datagen.flow_from_directory(
        config.VAL_DIR,
        target_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical'
    )

    # 2. Build Model
    print("🏗️ Model toiri hocche...")
    cnn_model = model_builder.build_model()

    # 3. Callbacks (Training control korar tools)
    
    # Val accuracy na barle training bondho korbe
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    # Best model ta save korbe
    checkpoint = ModelCheckpoint(config.MODEL_SAVE_PATH, monitor='val_accuracy', save_best_only=True)
    
    # Accuracy atke gele learning rate komiye dibe
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=0.00001)

    # 4. Start Training
    print(f"🚀 Training suru hocche... Total Epochs: {config.EPOCHS}")
    history = cnn_model.fit(
        train_generator,
        epochs=config.EPOCHS,
        validation_data=val_generator,
        callbacks=[early_stop, checkpoint, reduce_lr]
    )

    print(f"✅ Training Complete! Model save kora hoyeche: {config.MODEL_SAVE_PATH}")
    
    # Save Training History for Visualization
    import pickle
    history_path = config.HISTORY_SAVE_PATH
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, 'wb') as f:
        pickle.dump(history.history, f)
    print(f"📊 Training history save hoyeche: {history_path}")
    
    return history

if __name__ == "__main__":
    # Check jodi processed data thake
    if not os.path.exists(config.TRAIN_DIR):
        print("❌ Error: 'processed' data pawa jacche na. Age 'split_data.py' run korun!")
    else:
        train()