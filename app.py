import streamlit as st
import os
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image
import hashlib

# --- CONFIG ---
st.set_page_config(page_title="Face Attendance Pro", layout="wide")
DB_PATH = "attendance_system.db"
STUDENT_PATH = "students"

if not os.path.exists(STUDENT_PATH):
    os.makedirs(STUDENT_PATH)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  roll_no TEXT UNIQUE NOT NULL,
                  dept TEXT,
                  photo_path TEXT,
                  photo_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  roll_no TEXT,
                  name TEXT,
                  date TEXT,
                  time TEXT,
                  FOREIGN KEY(student_id) REFERENCES students(id))''')
    conn.commit()
    conn.close()

init_db()

# --- FUNCTIONS ---
def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def check_duplicate(hash_val, roll_no):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM students WHERE photo_hash=? OR roll_no=?", (hash_val, roll_no))
    data = c.fetchone()
    conn.close()
    return data

# --- SESSION FOR PROFILE ---
if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None

# --- SIDEBAR ---
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Go to", ["Home - Mark Attendance", "Register New Student", "View Attendance Sheet"])

# --- 1. HOME PAGE - CLICKABLE PROFILES ---
if menu == "Home - Mark Attendance":
    st.title("👋 Click on Your Photo to Mark Attendance")

    df = get_all_students()
    if df.empty:
        st.warning("No students registered yet! Go to Register page.")
    else:
        # If a profile is selected, show profile page
        if st.session_state.selected_student is not None:
            student = df[df['id'] == st.session_state.selected_student].iloc[0]
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(student['photo_path'], width=300)
                if st.button("⬅️ Back to All Students"):
                    st.session_state.selected_student = None
                    st.rerun()
            with col2:
                st.header(f"{student['name']}")
                st.write(f"**Roll No:** {student['roll_no']}")
                st.write(f"**Dept:** {student['dept']}")
                st.write(f"**ID:** {student['id']}")
                st.divider()
                if st.button("✅ MARK MY ATTENDANCE", type="primary", use_container_width=True):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    today = datetime.now().strftime("%Y-%m-%d")
                    # check if already marked today
                    c.execute("SELECT * FROM attendance WHERE roll_no=? AND date=?", (student['roll_no'], today))
                    if c.fetchone():
                        st.error(f"Already marked today!")
                    else:
                        now_time = datetime.now().strftime("%H:%M:%S")
                        c.execute("INSERT INTO attendance (student_id, roll_no, name, date, time) VALUES (?,?,?,?,?)",
                                  (int(student['id']), student['roll_no'], student['name'], today, now_time))
                        conn.commit()
                        st.success(f"Attendance Marked for {student['name']} at {now_time}!")
                        st.balloons()
                    conn.close()
        else:
            # Show all students as cards
            cols = st.columns(4)
            for index, row in df.iterrows():
                with cols[index % 4]:
                    st.image(row['photo_path'], use_container_width=True)
                    st.write(f"**{row['name']}**")
                    st.caption(f"{row['roll_no']}")
                    if st.button(f"View Profile", key=f"btn_{row['id']}", use_container_width=True):
                        st.session_state.selected_student = row['id']
                        st.rerun()
                    st.divider()

# --- 2. REGISTER PAGE ---
elif menu == "Register New Student":
    st.title("📝 Register New Student")
    name = st.text_input("Full Name")
    roll_no = st.text_input("Roll Number (Unique)")
    dept = st.text_input("Department")
    uploaded_file = st.file_uploader("Upload Face Photo", type=['jpg','png','jpeg'])

    if st.button("Register"):
        if not name or not roll_no or not uploaded_file:
            st.error("Fill all fields!")
        else:
            file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
            duplicate = check_duplicate(file_hash, roll_no)
            if duplicate:
                st.error(f"❌ Already registered! Same face or Roll No exists as: {duplicate[0]}")
            else:
                # save image
                save_path = os.path.join(STUDENT_PATH, f"{roll_no}_{uploaded_file.name}")
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO students (name, roll_no, dept, photo_path, photo_hash) VALUES (?,?,?,?,?)",
                          (name, roll_no, dept, save_path, file_hash))
                conn.commit()
                conn.close()
                st.success(f"✅ {name} registered successfully! Now go to Home to mark attendance.")
                st.balloons()

# --- 3. VIEW ATTENDANCE ---
else:
    st.title("📊 Attendance Sheet")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC, time DESC", conn)
    conn.close()
    if df.empty:
        st.info("No attendance yet.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False), "attendance.csv")
