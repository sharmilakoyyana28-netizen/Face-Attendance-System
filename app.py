import streamlit as st
import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime

# --- PASSWORD - CHANGE THIS ---
ADMIN_PASSWORD = "sharmila123"

FACE_DATA = "faces_data"
ATTENDANCE_FILE = "attendance.csv"

st.set_page_config(page_title="Face Attendance", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not os.path.exists(FACE_DATA):
    os.makedirs(FACE_DATA)

tab1, tab2, tab3 = st.tabs(["Register", "Attendance", "Sheet"])

# TAB 1 - REGISTER
with tab1:
    st.header("Register New Face (Admin Only)")
    
    if not st.session_state.authenticated:
        pwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Unlocked babe!")
                st.rerun()
            else:
                st.error("Wrong password!")
    else:
        st.success("Admin unlocked 🔓")
        name = st.text_input("Name", value="Sharmila Koyyana")
        roll = st.text_input("Roll Number", value="2454640062")
        
        img_file = st.camera_input("Take Photo")
        
        if img_file is not None:
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Fix for empty() error
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                st.error("No face found 😭 Come closer!")
            else:
                st.success(f"Face found! {len(faces)} face(s)")
                if st.button("Register Face"):
                    folder = os.path.join(FACE_DATA, f"{name}_{roll}")
                    os.makedirs(folder, exist_ok=True)
                    path = os.path.join(folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                    cv2.imwrite(path, cv2_img)
                    st.success(f"Registered {name}!")
        
        if st.button("Lock Again"):
            st.session_state.authenticated = False
            st.rerun()

# TAB 2 - ATTENDANCE (keep your code)
with tab2:
    st.header("Mark Attendance")
    st.write("Your attendance code here")

# TAB 3 - SHEET (keep your code)
with tab3:
    st.header("Attendance Sheet")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df)
        st.download_button("Download", df.to_csv(index=False), "attendance.csv")
    else:
        st.write("No attendance yet")
