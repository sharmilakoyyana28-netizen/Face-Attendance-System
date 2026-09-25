import streamlit as st
import os, sqlite3, hashlib, pandas as pd
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

# --- THEME FIX (Bring back your old theme) ---
st.set_page_config(page_title="Face Attendance", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #f8f9ff; }
div[data-testid="stImage"] { border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.stButton>button { border-radius: 10px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "attendance_system.db"
STUDENT_PATH = "students"
os.makedirs(STUDENT_PATH, exist_ok=True)

# --- DB ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY, name TEXT, roll_no TEXT UNIQUE, dept TEXT, photo_path TEXT, photo_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY, student_id INTEGER, roll_no TEXT, name TEXT, date TEXT, time TEXT)''')
    conn.commit()
    conn.close()
init_db()

def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None

# --- FACE MATCH FUNCTION (Simple & Works on Streamlit Cloud) ---
def verify_faces(stored_path, captured_file):
    try:
        # Try with face_recognition if available
        import face_recognition
        stored_img = face_recognition.load_image_file(stored_path)
        captured_img = face_recognition.load_image_file(captured_file)

        stored_enc = face_recognition.face_encodings(stored_img)
        captured_enc = face_recognition.face_encodings(captured_img)

        if len(stored_enc)==0 or len(captured_enc)==0:
            return False, 0
        result = face_recognition.compare_faces([stored_enc[0]], captured_enc[0], tolerance=0.5)
        distance = face_recognition.face_distance([stored_enc[0]], captured_enc[0])[0]
        score = (1-distance)*100
        return result[0], score
    except ImportError:
        # Fallback: If library not installed, use OpenCV similarity (for demo it will work)
        img1 = cv2.imread(stored_path, 0)
        img2 = Image.open(captured_file).convert('L')
        img2 = np.array(img2)
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        # Simple histogram compare
        score = cv2.compareHist(cv2.calcHist([img1],[0],None,[256],[0,256]), cv2.calcHist([img2],[0],None,[256],[0,256]), cv2.HISTCMP_CORREL)
