import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Face Attendance System")
st.title("Face Attendance System")

# Load cascade - with check
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if face_cascade.empty():
    st.error("Failed to load face detector!")
    st.stop()

img_file = st.camera_input("Take a photo")

if img_file is not None:
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if cv_img is None or cv_img.size == 0:
        st.error("Could not read image! Please try again!")
    else:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        if gray is None or gray.size == 0:
            st.error("Could not convert image!")
        else:
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                st.warning("No face detected! Try better light!")
                st.image(cv_img, channels="BGR")
            else:
                for (x, y, w, h) in faces:
                    cv2.rectangle(cv_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                st.image(cv_img, channels="BGR")
                st.success(f"Found {len(faces)} face(s)!")
else:
    st.info("Take a photo to start attendance babe!")
