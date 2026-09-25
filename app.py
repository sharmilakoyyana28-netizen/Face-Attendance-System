import streamlit as st
import os, sqlite3, hashlib, pandas as pd
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Face Attendance", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8f9ff; }
.stButton>button { border-radius: 10px; font-weight: 600; width: 100%; }
div[data-testid="stImage"] img { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "attendance_system.db"
STUDENT_PATH = "students"
os.makedirs(STUDENT_PATH, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, roll_no TEXT UNIQUE, dept TEXT, photo_path TEXT, photo_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, student_id INTEGER, roll_no TEXT, name TEXT, date TEXT, time TEXT)''')
    conn.commit()
    conn.close()
init_db()

def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def verify_faces_simple(stored_path, captured_file):
    try:
        img1 = cv2.imread(stored_path, 0)
        img2_pil = Image.open(captured_file).convert('L')
        img2 = np.array(img2_pil)
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        # Compare histograms
        hist1 = cv2.calcHist([img1],[0],None,[256],[0,256])
        hist2 = cv2.calcHist([img2],[0],None,[256],[0,256])
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
