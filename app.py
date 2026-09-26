import streamlit as st
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
            known_names.append(reg)
