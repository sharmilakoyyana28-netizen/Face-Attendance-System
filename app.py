import streamlit as st
import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Face Attendance", layout="centered")
st.title("Face Recognition Attendance")

ATTENDANCE_FILE = "attendance.csv"
FACES_DIR = "registered_faces"
os.makedirs(FACES_DIR, exist_ok=True)

st.header("1. Register")
name = st.text_input("Student Name")
img = st.file_uploader("Upload", type=["jpg","png","jpeg"])
cam1 = st.camera_input("Or Camera for Register")

if st.button("Register Face"):
    src = None
    if img: src = Image.open(img)
    elif cam1: src = Image.open(cam1)
    if name and src:
        src.save(os.path.join(FACES_DIR, name+".jpg"))
        st.success(f"{name} Registered!")
    else:
        st.warning("Give name + photo")

st.divider()
st.header("2. Mark Attendance with Face Match")

cam2 = st.camera_input("Take photo to Mark Attendance")

if st.button("Mark Attendance") and cam2:
    test_img = np.array(Image.open(cam2))
    test_gray = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)
    
    matched = None
    max_score = 0
    for file in os.listdir(FACES_DIR):
        ref = cv2.imread(os.path.join(FACES_DIR, file), 0)
        ref = cv2.resize(ref, (200,200))
        test_r = cv2.resize(test_gray, (200,200))
        score = cv2.matchTemplate(test_r, ref, cv2.TM_CCOEFF_NORMED).max()
        if score > max_score:
            max_score = score
            matched = file.replace(".jpg","")
    
    if matched and max_score > 0.5:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        if not os.path.exists(ATTENDANCE_FILE):
            pd.DataFrame(columns=["Name","Date","Time"]).to_csv(ATTENDANCE_FILE,index=False)
        df = pd.read_csv(ATTENDANCE_FILE)
        
        if not ((df['Name']==matched) & (df['Date']==date_str)).any():
            df.loc[len(df)] = [matched, date_str, time_str]
            df.to_csv(ATTENDANCE_FILE,index=False)
            st.success(f"Attendance Marked: {matched} ({max_score:.2f})")
            st.balloons()
        else:
            st.warning("Already Marked Today!")
    else:
        st.error(f"No Face Matched! Score: {max_score:.2f} - Register first!")

st.divider()
st.header("3. Sheet")
if os.path.exists(ATTENDANCE_FILE):
    st.dataframe(pd.read_csv(ATTENDANCE_FILE), use_container_width=True)
