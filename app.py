import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Face Attendance System")

st.title("Face Attendance System")

# Load cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

img_file = st.camera_input("Take a photo")

if img_file is not None:
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if cv_img is None:
        st.error("Failed to read image, try again!")
    else:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            st.warning("No face detected! Try again with better light!")
        else:
            for (x, y, w, h) in faces:
                cv2.rectangle(cv_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            st.image(cv_img, channels="BGR")
            st.success(f"Found {len(faces)} face(s)!")
            # Add your attendance marking code below here
