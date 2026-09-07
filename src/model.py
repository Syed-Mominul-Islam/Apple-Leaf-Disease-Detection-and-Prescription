import tensorflow as tf
from tensorflow.keras import layers, models
import config  # Amader banano config file import korlam

def build_model():
    # Model configuration check
    if config.MODEL_NAME == "appleNetV1":
        model = models.Sequential([
            # 1. First Convolutional Block
            layers.Conv2D(32, (3, 3), padding='same', input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS)),
            layers.BatchNormalization(), # Training fast kore
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),
            
            # 2. Second Convolutional Block
            layers.Conv2D(64, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),
            
            # 3. Third Convolutional Block
            layers.Conv2D(128, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),

            # 4. Fourth Convolutional Block (Deep Features)
            layers.Conv2D(256, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),

            # 5. Flatten & Dense Layers (Classification)
            layers.Flatten(),
            layers.Dense(512),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.5), # Overfitting komanor jonno

            # 6. Output Layer (7 Classes)
            layers.Dense(config.NUM_CLASSES, activation='softmax')
        ])
    else:
        # Pretrained Model Selection
        if config.MODEL_NAME == "mobilenetv2":
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        elif config.MODEL_NAME == "resnet50":
            base_model = tf.keras.applications.ResNet50(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        elif config.MODEL_NAME == "densenet121":
            base_model = tf.keras.applications.DenseNet121(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        elif config.MODEL_NAME == "efficientnetb0":
            base_model = tf.keras.applications.EfficientNetB0(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        elif config.MODEL_NAME == "vgg16":
            base_model = tf.keras.applications.VGG16(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        elif config.MODEL_NAME == "vgg19":
            base_model = tf.keras.applications.VGG19(
                input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.CHANNELS),
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unknown MODEL_NAME: {config.MODEL_NAME}")

        # Freeze base model layers
        base_model.trainable = False

        # Add Classification Head
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.5),
            layers.Dense(config.NUM_CLASSES, activation='softmax')
        ])

    # Model Compile
    optimizer = tf.keras.optimizers.Adam(learning_rate=config.LEARNING_RATE)
    
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

if __name__ == "__main__":
    # Test korar jonno (shudhu ei file run korle model summary dekhabe)
    model = build_model()
    model.summary()