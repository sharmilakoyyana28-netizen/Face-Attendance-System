import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import pickle

st.set_page_config(page_title="Face Attendance System", page_icon="👩‍🎓", layout="centered")

st.title("👩‍🎓 Face Attendance System")
st.markdown("Deployable version of your project")

# Load trainer
@st.cache_resource
def load_recognizer():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        if os.path.exists("trainer.yml"):
            recognizer.read("trainer.yml")
            return recognizer
    except Exception as e:
        st.error(f"Trainer load error: {e}")
    return None

def get_names():
    # Try to get names from dataset folders
    if os.path.exists("dataset"):
        names = os.listdir("dataset")
        # Create ID map
        return {i: name for i, name in enumerate(names)}
    return {}

recognizer = load_recognizer()
id_to_name = get_names()

menu = st.sidebar.selectbox("Menu", ["Mark Attendance", "View Attendance", "How to Register"])

if menu == "Mark Attendance":
    st.header("📸 Mark Your Attendance")
    st.write("Click photo - it will detect and mark attendance")
    
   img_file = st.camera_input("Take a photo")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if img_file is not None:
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if cv_img is None:
        st.error("Failed to read image, try again!")
    else:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            st.warning("No face detected! Try again with better light!")
        else:
            for (x,y,w,h) in faces:
                cv2.rectangle(cv_img, (x,y), (x+w, y+h), (0,255,0), 2)
            st.image(cv_img, channels="BGR")
                if recognizer:
                    id_pred, conf = recognizer.predict(gray[y:y+h, x:x+w])
                    # Lower confidence is better in LBPH
                    if conf < 80:
                        name = id_to_name.get(id_pred, f"User {id_pred}")
                        st.success(f"✅ Recognized: **{name}** (Confidence: {100-conf:.0f}%)")
                        
                        # Mark attendance
                        now = datetime.now()
                        date_str = now.strftime("%Y-%m-%d")
                        time_str = now.strftime("%H:%M:%S")
                        
                        file_path = "Attendance.csv"
                        # Create file if not exists
                        if not os.path.exists(file_path):
                            df = pd.DataFrame(columns=["Name", "Date", "Time"])
                            df.to_csv(file_path, index=False)
                        
                        df = pd.read_csv(file_path)
                        # Avoid duplicate same day
                        if not ((df['Name'] == name) & (df['Date'] == date_str)).any():
                            new_row = pd.DataFrame([{"Name": name, "Date": date_str, "Time": time_str}])
                            df = pd.concat([df, new_row], ignore_index=True)
                            df.to_csv(file_path, index=False)
                            st.balloons()
                            st.info(f"Attendance marked for {name} at {time_str}")
                        else:
                            st.info(f"{name} attendance already marked today!")
                    else:
                        st.error("❌ Unknown face! Please register first.")
                else:
                    st.warning("Trainer not found! Run collect_faces.py & train first locally.")
            
            st.image(cv_img, channels="BGR")

elif menu == "View Attendance":
    st.header("📋 Attendance Sheet")
    if os.path.exists("Attendance.csv"):
        df = pd.read_csv("Attendance.csv")
