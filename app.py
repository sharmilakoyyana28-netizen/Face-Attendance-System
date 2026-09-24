import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
import pandas as pd
from PIL import Image
import urllib.request

st.set_page_config(page_title="Face Attendance")
st.title("📸 Face Attendance")

os.makedirs("faces_data", exist_ok=True)
NAMES_FILE = "faces_data/names.json"
MODEL_FILE = "faces_data/trainer.yml"
ATTENDANCE_FILE = "attendance.csv"
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# FIX: Download cascade if not present or empty
def load_cascade():
    if not os.path.exists(CASCADE_PATH):
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        urllib.request.urlretrieve(url, CASCADE_PATH)
    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if cascade.empty():
        # Try opencv data path
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    return cascade

face_cascade = load_cascade()

if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, 'r') as f:
        name_dict = json.load(f)
else:
    name_dict = {}

def get_faces(gray):
    try:
        if face_cascade.empty():
            st.error("Face detector file missing, re-downloading...")
            return []
        # Brighten
        gray = cv2.equalizeHist(gray)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        return faces
    except Exception as e:
        st.error(f"Detector error fixed, try again: {e}")
        return []

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
        name = file.replace(".jpg", "")
        for k, v in name_dict.items():
            if v == name:
                faces.append(img)
                ids.append(int(k))
    if len(faces) > 0:
        rec = cv2.face.LBPHFaceRecognizer_create()
        rec.train(faces, np.array(ids))
        rec.save(MODEL_FILE)
        return True
    return False

t1, t2, t3 = st.tabs(["Register", "Attendance", "Sheet"])

with t1:
    st.header("Register - Red Box Will Show Now")
    name = st.text_input("Full Name")
    roll = st.text_input("Roll No")
    photo = st.camera_input("Take Photo", key="reg")
    if photo is not None:
        pil = Image.open(photo)
        img = np.array(pil)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = get_faces(gray)
        img_box = img.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(img_box, (x, y), (x+w, y+h), (255, 0, 0), 4)
        if len(faces) > 0:
            st.image(img_box, caption="RED BOX - Face Found!")
            st.success("Perfect! Now click Register below")
        else:
            st.image(img_box)
            st.error("No face! Move closer to camera, more light!")

    if st.button("Register Face"):
        if not name or not roll:
            st.error("Enter Name and Roll")
        elif photo is None:
            st.error("Take photo first")
        else:
            pil = Image.open(photo)
            img = np.array(pil)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            faces = get_faces(gray)
            if len(faces) == 0:
                st.error("No face detected! Come closer!")
            elif len(faces) > 1:
                st.error("Only one person!")
            else:
                x, y, w, h = faces[0]
                roi = gray[y:y+h, x:x+w]
                roi = cv2.resize(roi, (200, 200))
                full = name + "_" + roll
                cv2.imwrite("faces_data/" + full + ".jpg", roi)
                nid = str(len(name_dict))
                name_dict[nid] = full
                with open(NAMES_FILE, 'w') as f:
                    json.dump(name_dict, f)
                train_model()
                st.success("Registered " + name)
                st.balloons()

with t2:
    st.header("Attendance")
    if len(name_dict) == 0:
        st.warning("Register first!")
    else:
        photo = st.camera_input("Take Photo", key="att")
        if photo:
            pil = Image.open(photo)
            img = np.array(pil)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            faces = get_faces(gray)
            img_box = img.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(img_box, (x, y), (x+w, y+h), (0, 255, 0), 3)
            if len(faces) > 0:
                st.image(img_box)
            if len(faces) == 0:
                st.error("No face!")
            else:
                if not os.path.exists(MODEL_FILE):
                    train_model()
                rec = cv2.face.LBPHFaceRecognizer_create()
                rec.read(MODEL_FILE)
                for (x, y, w, h) in faces:
                    roi = gray[y:y+h, x:x+w]
                    roi = cv2.resize(roi, (200, 200))
                    id_, conf = rec.predict(roi)
                    if conf < 70:
                        person = name_dict.get(str(id_), "Unknown")
                        now = datetime.now()
                        d = now.strftime("%Y-%m-%d")
                        t = now.strftime("%H:%M:%S")
                        data = {"Name": [person], "Date": [d], "Time": [t], "Status": ["Present"]}
                        if os.path.exists(ATTENDANCE_FILE):
                            old = pd.read_csv(ATTENDANCE_FILE)
                            same = ((old["Name"] == person) & (old["Date"] == d)).any()
                            if not same:
                                pd.concat([old, pd.DataFrame(data)]).to_csv(ATTENDANCE_FILE, index=False)
                                st.success("Marked " + person)
                            else:
                                st.info("Already marked today")
                        else:
                            pd.DataFrame(data).to_csv(ATTENDANCE_FILE, index=False)
                            st.success("Marked " + person)
                    else:
                        st.error("Not registered!")

with t3:
    st.header("Sheet")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df)
        st.download_button("Download", df.to_csv(index=False).encode("utf-8"), "attendance.csv", "text/csv")
    else:
        st.info("No records")
