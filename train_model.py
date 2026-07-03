import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os

print("Preparing dataset...")

# Dataset path
dataset_path = "raw/color"

# Image settings
IMG_SIZE = 128
BATCH_SIZE = 32

# Data augmentation + validation split
train_datagen = ImageDataGenerator(

    rescale=1./255,

    validation_split=0.2,

    rotation_range=20,

    zoom_range=0.2,

    horizontal_flip=True,

    shear_range=0.2

)

# Training data
train_generator = train_datagen.flow_from_directory(

    dataset_path,

    target_size=(IMG_SIZE, IMG_SIZE),

    batch_size=BATCH_SIZE,

    class_mode='sparse',

    subset='training'

)

# Validation data
validation_generator = train_datagen.flow_from_directory(

    dataset_path,

    target_size=(IMG_SIZE, IMG_SIZE),

    batch_size=BATCH_SIZE,

    class_mode='sparse',

    subset='validation'

)

# Total classes
num_classes = len(train_generator.class_indices)

print("Total Classes:", num_classes)

print("Building CNN model...")

# CNN Model
model = models.Sequential([

    layers.Input(shape=(128, 128, 3)),

    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),

    layers.Dense(256, activation='relu'),

    layers.Dropout(0.5),

    layers.Dense(num_classes, activation='softmax')

])

# Compile model
model.compile(

    optimizer='adam',

    loss='sparse_categorical_crossentropy',

    metrics=['accuracy']

)

print("Training started...")

# Train model
history = model.fit(

    train_generator,

    validation_data=validation_generator,

    epochs=10

)

# Create model folder
os.makedirs("model", exist_ok=True)

print("Saving model...")

# Save model
model.save("model/best_plant_disease_model.keras")

# Save class names
with open("model/class_names.txt", "w") as f:

    for class_name in train_generator.class_indices.keys():

        f.write(class_name + "\n")

print("Training completed successfully!")

print("Model saved at:")
print("model/best_plant_disease_model.keras")