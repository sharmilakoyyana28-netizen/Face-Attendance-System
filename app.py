import streamlit as st
import cv2
import face_recognition
import numpy as np
import os
import pickle
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Face Attendance System", layout="centered")
st.title("📸 Face Attendance System")

# Files
ENCODINGS_FILE = "encodings.pkl"
ATTENDANCE_FILE = "attendance.csv"

# Load data
if os.path.exists(ENCODINGS_FILE):
    with open(ENCODINGS_FILE, 'rb') as f:
        known_encodings, known_names = pickle.load(f)
else:
    known_encodings, known_names = [], []

# --- Register Section ---
st.header("1. Register Student")
reg_name = st.text_input("Enter Student Name")
reg_image = st.file_uploader("Upload Student Photo", type=["jpg", "jpeg", "png"])

if st.button("Register"):
    if reg_name and reg_image:
        image = face_recognition.load_image_file(reg_image)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(reg_name)
            with open(ENCODINGS_FILE, 'wb') as f:
                pickle.dump((known_encodings, known_names), f)
            st.success(f"{reg_name} Registered Successfully!")
        else:
            st.error("No face detected in image!")
    else:
        st.warning("Please enter name and upload photo")

st.divider()

# --- Attendance Section ---
st.header("2. Mark Attendance")
cam_image = st.camera_input("Take a photo for attendance")

if cam_image:
    image = face_recognition.load_image_file(cam_image)
    face_encodings = face_recognition.face_encodings(image)
    face_locations = face_recognition.face_locations(image)

    if not face_encodings:
        st.error("No face detected!")
    else:
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

                # Save attendance
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")

                if not os.path.exists(ATTENDANCE_FILE):
                    df = pd.DataFrame(columns=["Name", "Date", "Time"])
                    df.to_csv(ATTENDANCE_FILE, index=False)

                df = pd.read_csv(ATTENDANCE_FILE)
                # Check if already marked today
                if not ((df['Name'] == name) & (df['Date'] == date_str)).any():
                    new_row = pd.DataFrame([[name, date_str, time_str]], columns=["Name", "Date", "Time"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(ATTENDANCE_FILE, index=False)
                    st.success(f"Attendance Marked for {name} at {time_str}")
                else:
                    st.warning(f"{name} - Attendance already marked today!")

            else:
                st.error("Unknown Person!")

st.divider()

# --- View Attendance ---
st.header("3. Attendance Sheet")
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
    st.dataframe(df)
else:
    st.info("No attendance records yet")

st.divider()
st.write(f"Total Registered: {len(known_names)}")
st.write(known_names)
