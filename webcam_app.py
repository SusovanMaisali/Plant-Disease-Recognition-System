import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from PIL import Image

# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="Live Plant Disease Detection",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 Live Webcam Disease Detection")

st.write(
    "Realtime Plant Disease Detection using Webcam"
)

# --------------------------------
# LOAD MODEL
# --------------------------------

model = tf.keras.models.load_model(
    "model/best_plant_disease_model.keras"
)

# --------------------------------
# LOAD CLASS NAMES
# --------------------------------

with open("model/class_names.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

# --------------------------------
# LEAF VALIDATION
# --------------------------------

def is_leaf(frame):

    green_pixels = np.sum(
        (frame[:, :, 1] > frame[:, :, 0]) &
        (frame[:, :, 1] > frame[:, :, 2])
    )

    total_pixels = frame.shape[0] * frame.shape[1]

    ratio = green_pixels / total_pixels

    return ratio > 0.15

# --------------------------------
# VIDEO PROCESSOR
# --------------------------------

class VideoProcessor(VideoTransformerBase):

    def transform(self, frame):

        img = frame.to_ndarray(format="bgr24")

        display_img = img.copy()

        # Resize for prediction
        resized = cv2.resize(img, (128, 128))

        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Leaf check
        if is_leaf(rgb):

            # Normalize
            rgb = rgb / 255.0

            rgb = np.expand_dims(rgb, axis=0)

            # Prediction
            prediction = model.predict(rgb, verbose=0)

            predicted_class = np.argmax(prediction)

            confidence = np.max(prediction) * 100

            disease = class_names[predicted_class]

            # Display prediction
            text = f"{disease} ({confidence:.2f}%)"

            cv2.putText(
                display_img,
                text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        else:

            cv2.putText(
                display_img,
                "Show Plant Leaf",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        return display_img

# --------------------------------
# START WEBCAM
# --------------------------------

webrtc_streamer(
    key="plant-disease-detection",
    video_transformer_factory=VideoProcessor,
    media_stream_constraints={
        "video": True,
        "audio": False
    },
    async_processing=True,
)

# --------------------------------
# FOOTER
# --------------------------------

st.markdown("---")

st.caption(
    "AI Powered Realtime Plant Disease Detection"
)