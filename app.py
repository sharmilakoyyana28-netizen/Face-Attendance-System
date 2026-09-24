import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Face Attendance")
st.title("📸 Face Attendance with Detection")

os.makedirs("faces_data", exist_ok=True)
NAMES_FILE = "faces_data/names.json"
MODEL_FILE = "faces_data/trainer.yml"
ATTENDANCE_FILE = "attendance.csv"

if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, 'r') as f:
        name_dict = json.load(f)
else:
    name_dict = {}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    'haarcascade_frontalface_default.xml'
)

def detect_faces(img):
    try:
        if img is None:
            return [], None, None
        # Keep color copy for drawing red box
        if len(img.shape) == 3:
            color_img = img.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            gray = img
        if gray is None or gray.size == 0:
            return [], None, None
        # Brighten dark images
        gray_eq = cv2.equalizeHist(gray)
        faces = face_cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(30, 30)
        )
        return faces, gray, color_img
    except Exception as e:
        print(e)
        return [], None, None

def train_model():
    faces = []
    ids = []
    for file in os.listdir("faces_data"):
        if not file.endswith(".jpg"):
            continue
        path = os.path.join("faces_data", file)
        img = cv2.imread(path, 0)
        if img is None:
            continue
        for nid, nname in name_dict.items():
            if nname == file.replace(".jpg", ""):
                faces.append(img)
                ids.append(int(nid))
    if len(faces) > 0:
        rec = cv2.face.LBPHFaceRecognizer_create()
        rec.train(faces, np.array(ids))
        rec.save(MODEL_FILE)
        return True
    return False

tab1, tab2, tab3 = st.tabs(
    ["📝 Register", "✅ Attendance", "📊 Sheet"]
)

with tab1:
    st.header("Register Face")
    reg_name = st.text_input("Name")
    reg_roll = st.text_input("Roll No")
    reg_image = st.camera_input("Take Photo", key="reg")

    if reg_image:
        pil_img = Image.open(reg_image)
        img = np.array(pil_img)
        faces, gray, color_img = detect_faces(img)

        # DRAW RED BOX HERE BABE ❤️
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(
                    color_img,
                    (x, y),
                    (x+w, y+h),
                    (255, 0, 0),
                    3
                )
                cv2.putText(
                    color_img,
                    "Face Detected",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2
                )
            st.image(color_img, caption="Red Box = Face Found!")
            st.success(f"Found {len(faces)} face(s)! Now click Register!")
        else:
            st.image(color_img)
            st.error("No face! Come closer, good light!")

    if st.button("Register Face"):
        if not reg_name or not reg_roll:
            st.error("Enter Name and Roll!")
        elif reg_image is None:
            st.error("Take Photo first!")
        else:
            pil_img = Image.open(reg_image)
            img = np.array(pil_img
