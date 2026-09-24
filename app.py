import streamlit as st
import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime

ADMIN_PASSWORD = "sharmila123" # your password

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
                st.rerun()
            else:
                st.error("Wrong password!")
    else:
        st.success("Admin unlocked 🔓")
        name = st.text_input("Name")
        roll = st.text_input("Roll Number")
        img_file = st.camera_input("Take Photo for Register", key="reg")
        if img_file is not None:
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            st.image(cv2_img, channels="BGR")
            if st.button("Register Face"):
                folder = os.path.join(FACE_DATA, f"{name}_{roll}")
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(path, cv2_img)
                st.success(f"Registered {name}!")
                st.balloons()
        if st.button("Lock Again"):
            st.session_state.authenticated = False
            st.rerun()

# TAB 2 - ATTENDANCE (WORKING!)
with tab2:
    st.header("Mark Attendance")

    # Show registered students
    registered = os.listdir(FACE_DATA) if os.path.exists(FACE_DATA) else []
    if not registered:
        st.warning("No students registered yet! Go to Register tab")
    else:
        st.write(f"Registered: {', '.join(registered)}")
        img_file = st.camera_input("Take Photo for Attendance", key="att")
        selected = st.selectbox("Select your name", registered)

        if img_file is not None and st.button("Mark Present"):
            now = datetime.now()
            data = {
                "Name_Roll": selected,
                "Date": now.strftime("%Y-%m-%d"),
                "Time": now.strftime("%H:%M:%S"),
                "Status": "Present"
            }
            if os.path.exists(ATTENDANCE_FILE):
                df = pd.read_csv(ATTENDANCE_FILE)
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            else:
                df = pd.DataFrame([data])
            df.to_csv(ATTENDANCE_FILE, index=False)
            st.success(f"Attendance marked for {selected}! ✅")
            st.balloons()

# TAB 3 - SHEET
with tab3:
    st.header("Attendance Sheet")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "attendance.csv", mime="text/csv")
    else:
        st.info("No attendance yet")
