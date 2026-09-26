import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Face Attendance System", layout="centered")
st.title("Face Attendance System")

ATTENDANCE_FILE = "attendance.csv"
FACES_DIR = "registered_faces"
os.makedirs(FACES_DIR, exist_ok=True)

st.header("1. Register Student")
reg_name = st.text_input("Enter Student Name")
reg_image = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
cam_reg = st.camera_input("Or Take Photo for Registration")

if st.button("Register"):
    img_to_save = None
    if reg_image:
        img_to_save = Image.open(reg_image)
    elif cam_reg:
        img_to_save = Image.open(cam_reg)
    
    if reg_name and img_to_save:
        save_path = os.path.join(FACES_DIR, reg_name + ".jpg")
        img_to_save.save(save_path)
        st.success(reg_name + " Registered Successfully!")
    else:
        st.warning("Please enter name and give photo")

st.divider()

st.header("2. Mark Attendance")
files = os.listdir(FACES_DIR)
attendance_name = st.selectbox("Select Your Name", files if files else ["No Registered Users"])
cam_att = st.camera_input("Take photo for attendance")

if st.button("Mark Attendance"):
    if attendance_name != "No Registered Users" and cam_att:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        name_clean = attendance_name.replace(".jpg","")

        if not os.path.exists(ATTENDANCE_FILE):
            df = pd.DataFrame(columns=["Name", "Date", "Time"])
            df.to_csv(ATTENDANCE_FILE, index=False)
        
        df = pd.read_csv(ATTENDANCE_FILE)
        already = False
        if len(df) > 0:
            already = ((df['Name'] == name_clean) & (df['Date'] == date_str)).any()
        
        if not already:
            df.loc[len(df)] = [name_clean, date_str, time_str]
            df.to_csv(ATTENDANCE_FILE, index=False)
            st.success("Attendance Marked for " + name_clean + " at " + time_str)
            st.balloons()
        else:
            st.warning(name_clean + " - Already marked today!")
    else:
        st.error("Select name and take photo!")

st.divider()

st.header("3. Attendance Sheet")
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No records yet")

registered = [f.replace('.jpg','') for f in os.listdir(FACES_DIR)]
st.write("Total Registered: " + str(len(registered)))
st.write(registered)
