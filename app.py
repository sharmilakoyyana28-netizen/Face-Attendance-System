import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Face Attendance System", layout="centered")
st.title("📸 Smart Face Attendance System")

os.makedirs("faces_data", exist_ok=True)
NAMES_FILE = "faces_data/names.json"
MODEL_FILE = "faces_data/trainer.yml"
ATTENDANCE_FILE = "attendance.csv"

if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, 'r') as f:
        name_dict = json.load(f)
else:
    name_dict = {}

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(img):
    if img is None:
        return [], None
    # Fix RGBA and RGB
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
    if gray is None or gray.size == 0:
        return [], None
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    return faces, gray

def train_model():
    faces=[]; ids=[]
    for file in os.listdir("faces_data"):
        if file.endswith(".jpg"):
            path=os.path.join("faces_data", file)
            img=cv2.imread(path, 0)
            if img is None: continue
            for nid, nname in name_dict.items():
                if nname == file.replace(".jpg",""):
                    faces.append(img); ids.append(int(nid)); break
    if len(faces)>0:
        recognizer=cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))
        recognizer.save(MODEL_FILE)
        return True
    return False

tab1, tab2, tab3 = st.tabs(["📝 Register", "✅ Attendance", "📊 Sheet"])

with tab1:
    st.header("Register New Face")
    reg_name=st.text_input("Enter Full Name")
    reg_roll=st.text_input("Enter Roll No / ID")
    reg_image=st.camera_input("Take photo for Registration", key="reg")
    if st.button("Register Face"):
        if not reg_name or not reg_roll:
            st.error("Please enter Name and Roll No!")
        elif reg_image is None:
            st.error("Please take a photo first!")
        else:
            # FIXED: Use getvalue() not read()
            file_bytes = np.frombuffer(reg_image.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            faces, gray = detect_faces(img)
            if len(faces)==0:
                st.error("No face found! Come closer, good light!")
            elif len(faces)>1:
                st.error(f"Found {len(faces)} faces! Register alone!")
            else:
                x,y,w,h=faces[0]
                face_roi=gray[y:y+h, x:x+w]
                face_roi=cv2.resize(face_roi, (200,200))
                full_name=f"{reg_name}_{reg_roll}"
                cv2.imwrite(f"faces_data/{full_name}.jpg", face_roi)
                new_id=len(name_dict)
                name_dict[str(new_id)]=full_name
                with open(NAMES_FILE,'w') as f: json.dump(name_dict,f)
                train_model()
                st.success(f"✅ Registered! Welcome {reg_name}!")
                st.balloons()

with tab2:
    st.header("Mark Attendance")
    if len(name_dict)==0:
        st.warning("No faces yet! Register first!")
    else:
        att_image=st.camera_input("Take photo for Attendance", key="att")
        if att_image:
            file_bytes = np.frombuffer(att_image.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            faces, gray = detect_faces(img)
            if len(faces)==0:
                st.error("No face detected!")
            else:
                if not os.path.exists(MODEL_FILE): train_model()
                recognizer=cv2.face.LBPHFaceRecognizer_create()
                recognizer.read(MODEL_FILE)
                for (x,y,w,h) in faces:
                    roi=cv2.resize(gray[y:y+h, x:x+w], (200,200))
                    id_, conf = recognizer.predict(roi)
                    if conf < 70:
                        person=name_dict.get(str(id_),"Unknown")
                        now=datetime.now()
                        data={"Name":[person],"Date":[now.strftime("%Y-%m-%d")],"Time":[now.strftime("%H:%M:%S")],"Status":["Present"]}
                        if os.path.exists(ATTENDANCE_FILE):
                            df_old=pd.read_csv(ATTENDANCE_FILE)
                            if not ((df_old['Name']==person) & (df_old['Date']==now.strftime("%Y-%m-%d"))).any():
                                pd.concat([df_old, pd.DataFrame(data)]).to_csv(ATTENDANCE_FILE,index=False)
                                st.success(f"✅ Attendance Marked! Welcome {person}!")
                            else:
                                st.info(f"{person} already marked today!")
                        else:
                            pd.DataFrame(data).to_csv(ATTENDANCE_FILE,index=False)
                            st.success(f"✅ Attendance Marked! {person}!")
                    else:
                        st.error("❌ Face Not Registered!")

with tab3:
    st.header("Attendance Records")
    if os.path.exists(ATTENDANCE_FILE):
        df=pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "attendance.csv", "text/csv")
    else:
        st.info("No attendance yet!")
