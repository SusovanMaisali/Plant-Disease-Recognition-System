import tensorflow as tf

print("Loading Keras 3 model...")
try:
    model = tf.keras.models.load_model("model/best_plant_disease_model.keras")
    print("Model loaded successfully.")
    
    # Save as Legacy HDF5 format which is fully backward & forward compatible
    legacy_path = "model/best_plant_disease_model.h5"
    print(f"Saving model in legacy HDF5 format to: {legacy_path} ...")
    model.save(legacy_path)
    print("Saved successfully!")
except Exception as e:
    print(f"Error during model conversion: {e}")
