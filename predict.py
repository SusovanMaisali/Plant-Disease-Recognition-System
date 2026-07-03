import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os

# Load trained model
model = tf.keras.models.load_model(
    "model/best_plant_disease_model.keras"
)

# Load class names
with open("model/class_names.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

# Image size
IMG_SIZE = 128

# Enter image path here
image_path = input("Enter image path: ")

# Check file exists
if not os.path.exists(image_path):
    print("Image not found!")
    exit()

# Load image
img = Image.open(image_path).convert("RGB")

# Resize image
img = img.resize((IMG_SIZE, IMG_SIZE))

# Convert image to array
img_array = image.img_to_array(img)

# Normalize image
img_array = img_array / 255.0

# Add batch dimension
img_array = np.expand_dims(img_array, axis=0)

print("\nPredicting disease...\n")

# Prediction
prediction = model.predict(img_array)

# Get highest confidence class
predicted_index = np.argmax(prediction)

# Get confidence
confidence = np.max(prediction) * 100

# Get disease name
disease_name = class_names[predicted_index]

# Final output
print("Prediction Result")
print("-------------------")
print("Disease:", disease_name)
print(f"Confidence: {confidence:.2f}%")