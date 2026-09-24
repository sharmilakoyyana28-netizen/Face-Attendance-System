import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Face Attendance")
st.title("📸 Face Attendance")

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
            return [], None
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        if gray is None or gray.size == 0:
            return [], None
        # Make face brighter for detection
        gray = cv2.equalizeHist(gray)
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.05, 
            minNeighbors=3, 
            minSize=(30, 30)
        )
        return faces, gray
    except:
        return [], None
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
    ["Register", "Attendance", "Sheet"]
)

with tab1:
    st.header("Register Face")
    reg_name = st.text_input("Name")
    reg_roll = st.text_input("Roll No")
    reg_image = st.camera_input("Photo", key="reg")
    if st.button("Register Face"):
        if not reg_name or not reg_roll:
            st.error("Enter Name and Roll!")
        elif reg_image is None:
            st.error("Take Photo!")
        else:
            pil_img = Image.open(reg_image)
            img = np.array(pil_img)
            faces, gray = detect_faces(img)
            if len(faces) == 0:
                st.error("No face! Come closer!")
            elif len(faces) > 1:
                st.error("Only 1 face!")
            else:
                x, y, w, h = faces[0]
                roi = gray[y:y+h, x:x+w]
                roi = cv2.resize(roi, (200, 200))
                full_name = reg_name + "_" + reg_roll
                cv2.imwrite(
                    "faces_data/" + full_name + ".jpg",
                    roi
                )
                new_id = len(name_dict)
                name_dict[str(new_id)] = full_name
                with open(NAMES_FILE, 'w') as f:
                    json.dump(name_dict, f)
                train_model()
                st.success("Registered! " + reg_name)
                st.balloons()

with tab2:
    st.header("Take Attendance")
    if len(name_dict) == 0:
        st.warning("Register first!")
    else:
        att_image = st.camera_input(
            "Photo", key="att"
        )
        if att_image:
            pil_img = Image.open(att_image)
            img = np.array(pil_img)
            faces, gray = detect_faces(img)
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
                        person = name_dict.get(
                            str(id_), "Unknown"
                        )
                        now = datetime.now()
                        d = now.strftime("%Y-%m-%d")
                        t = now.strftime("%H:%M:%S")
                        data = {
                            "Name": [person],
                            "Date": [d],
                            "Time": [t],
                            "Status": ["Present"]
                        }
                        if os.path.exists(ATTENDANCE_FILE):
                            df_old = pd.read_csv(
                                ATTENDANCE_FILE
                            )
                            check = (
                                (df_old['Name'] == person) &
                                (df_old['Date'] == d)
                            ).any()
                            if not check:
                                df_new = pd.concat(
                                    [df_old, pd.DataFrame(data)]
                                )
                                df_new.to_csv(
                                    ATTENDANCE_FILE,
                                    index=False
                                )
                                st.success("Marked! " + person)
                            else:
                                st.info("Already marked!")
                        else:
                            pd.DataFrame(data).to_csv(
                                ATTENDANCE_FILE,
                                index=False
                            )
                            st.success("Marked! " + person)
                    else:
                        st.error("Not Registered!")

with tab3:
    st.header("Sheet")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode('utf-8'),
            "attendance.csv",
            "text/csv"
        )
    else:
        st.info("No data yet!")
