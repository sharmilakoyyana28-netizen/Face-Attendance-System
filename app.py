import streamlit as st
import os, sqlite3, hashlib, pandas as pd
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Face Attendance", layout="wide")
DB_PATH = "attendance_system.db"
STUDENT_PATH = "students"
os.makedirs(STUDENT_PATH, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, roll_no TEXT UNIQUE, dept TEXT, photo_path TEXT, photo_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, student_id INTEGER, roll_no TEXT, name TEXT, date TEXT, time TEXT)''')
    conn.commit(); conn.close()
init_db()

def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def verify_faces_simple(stored_path, captured_file):
    img1 = cv2.imread(stored_path, 0)
    img2 = np.array(Image.open(captured_file).convert('L'))
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    h1 = cv2.calcHist([img1],[0],None,[256],[0,256])
    h2 = cv2.calcHist([img2],[0],None,[256],[0,256])
    score = cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)
    return (score*100 > 65, score*100)

if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None

menu = st.sidebar.radio("Menu", ["Home - Mark Attendance", "Register New Student", "View Attendance Sheet"])

if menu == "Home - Mark Attendance":
    st.title("Click Your Photo for Face ID Check")
    df = get_all_students()
    if df.empty:
        st.warning("No students!")
    else:
        if st.session_state.selected_student is not None:
            student = df[df['id'] == st.session_state.selected_student].iloc[0]
            c1, c2 = st.columns([1,2])
            with c1:
                st.image(student['photo_path'], width=350)
                if st.button("⬅️ Back to All"):
                    st.session_state.selected_student = None
                    st.rerun()
                # DELETE BUTTON IN PROFILE
                if st.button("🗑️ Delete This Student", type="primary"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM students WHERE id=?", (int(student['id']),))
                    conn.commit(); conn.close()
                    try: os.remove(student['photo_path'])
                    except: pass
                    st.session_state.selected_student = None
                    st.success("Deleted!"); st.rerun()
            with c2:
                st.header(student['name'])
                cam = st.camera_input("Show your face")
                if cam:
                    ok, score = verify_faces_simple(student['photo_path'], cam)
                    st.write(f"Match Score: {score:.1f}%")
                    if ok:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        today = datetime.now().strftime("%Y-%m-%d")
                        c.execute("SELECT * FROM attendance WHERE roll_no=? AND date=?", (student['roll_no'], today))
                        if c.fetchone(): st.error("Already marked!")
                        else:
                            now = datetime.now().strftime("%H:%M:%S")
                            c.execute("INSERT INTO attendance (student_id, roll_no, name, date, time) VALUES (?,?,?,?,?)", (int(student['id']), student['roll_no'], student['name'], today, now))
                            conn.commit(); st.success("Attendance Marked!"); st.balloons()
                        conn.close()
                    else: st.error("Face Not Matching! Register with close-up photo.")
        else:
            cols = st.columns(4)
            for i, row in df.iterrows():
                with cols[i % 4]:
                    st.image(row['photo_path'], use_container_width=True)
                    st.markdown(f"**{row['name']}**")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Open", key=f"op_{row['id']}"):
                            st.session_state.selected_student = row['id']; st.rerun()
                    with b2:
                        if st.button("Delete", key=f"del_{row['id']}"):
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("DELETE FROM students WHERE id=?", (int(row['id']),))
                            conn.commit(); conn.close()
                            try: os.remove(row['photo_path'])
                            except: pass
                            st.rerun()

elif menu == "Register New Student":
    st.title("Register")
    name = st.text_input("Name"); roll_no = st.text_input("Roll No"); dept = st.text_input("Dept")
    file = st.file_uploader("Upload Close-up Face Photo", type=['jpg','png','jpeg'])
    if st.button("Register"):
        if not name or not roll_no or not file: st.error("Fill all!")
        else:
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("SELECT * FROM students WHERE roll_no=?", (roll_no,))
            if c.fetchone(): st.error("Roll No exists!")
            else:
                h = hashlib.md5(file.getvalue()).hexdigest()
                path = os.path.join(STUDENT_PATH, f"{roll_no}_{file.name}")
                with open(path, "wb") as f: f.write(file.getbuffer())
                c.execute("INSERT INTO students (name, roll_no, dept, photo_path, photo_hash) VALUES (?,?,?,?,?)", (name, roll_no, dept, path, h))
                conn.commit(); st.success("Registered!")
            conn.close()
else:
    st.title("Attendance Sheet")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "attendance.csv", mime="text/csv")
