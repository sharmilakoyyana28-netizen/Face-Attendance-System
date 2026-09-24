import streamlit as st
import cv2
import numpy as np
import os

st.set_page_config(page_title="Face Attendance System")
st.title("Face Attendance System")

# Load from uploaded file
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

if face_cascade.empty():
    st.error("Failed to load detector! Check xml file!")
    st.stop()

st.success("Detector ready!")

img_file = st.camera_input("Take a photo")

if img_file is not None:
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if cv_img is None:
        st.error("Could not read image!")
    else:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 6, minSize=(120,120))
        
        if len(faces) == 0:
            st.warning("No face detected!")
            st.image(cv_img, channels="BGR")
        else:
            for (x, y, w, h) in faces:
                cv2.rectangle(cv_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            st.image(cv_img, channels="BGR")
            st.success(f"Found {len(faces)} face(s)! Attendance Marked!")
