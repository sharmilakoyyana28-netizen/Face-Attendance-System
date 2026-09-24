import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Face Attendance System", layout="centered")
st.title("📸 Smart Face Attendance System")

# Create folders
os.makedirs("faces_data", exist_ok=True)
NAMES_FILE = "faces_data/names.json"
MODEL_FILE = "faces_data/trainer.yml"
ATTENDANCE_FILE = "attendance.csv"

# Load names
if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, 'r') as f:
        name_dict = json.load(f)
else:
    name_dict = {}

# --- FACE DETECTOR ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 10, minSize=(120, 120))
    return faces, gray

def train_model():
    faces = []
    ids = []
    labels = {}
    current_id = 0

    for file in os.listdir("faces_data"):
        if file.endswith(".jpg"):
            path = os.path.join("faces_data", file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            # name is filename without.jpg -> name_roll
            name_key = file.replace(".jpg", "")
            if name_key not in labels.values():
                # Assign id
                pass

            # Get ID from names.json reverse lookup
            for nid, nname in name_dict.items():
                if nname == file.replace(".jpg",""):
                    faces.append(img)
                    ids.append(int(nid))
                    break

    if len(faces) > 0:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))
        recognizer.save(MODEL_FILE)
        return True
    return False

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📝 Register", "✅ Take Attendance", "📊 Attendance Sheet"])

with tab1:
    st.header("Register New Face")
    st.write("Firstly register your face with Name!")

    reg_name = st.text_input("Enter Your Full Name")
    reg_roll = st.text_input("Enter Roll No / ID")

    reg_image = st.camera_input("Take photo for Registration", key="reg")

    if reg_image and reg_name and reg_roll:
        if st.button("Register Face"):
            # Process image
            file_bytes = np.asarray(bytearray(reg_image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            faces, gray = detect_faces(img)

            if len(faces) == 0:
                st.error("No face found! Please try again with clear light babe!")
            elif len(faces) > 1:
                st.error(f"Found {len(faces)} faces! Please register alone!")
            else:
                (x,y,w,h) = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (200,200))

                full_name = f"{reg_name}_{reg_roll}"
                save_path = f"faces_data/{full_name}.jpg"
                cv2.imwrite(save_path, face_roi)

                # Save name with new ID
                new_id = len(name_dict)
                name_dict[str(new_id)] = full_name
                with open(NAMES_FILE, 'w') as f:
                    json.dump(name_dict, f)

                # Train model
                if train_model():
                    st.success(f"✅ Registered Successfully! Welcome {reg_name}!")
                    st.balloons()
                else:
                    st.success(f"✅ First face registered! {reg_name}")
            # show cropped face
            st.image(face_roi, caption="Registered Face", width=200)
    else:
        st.info("Enter Name + Roll No and take photo to enable Register button")

with tab2:
    st.header("Mark Your Attendance")
    st.write("Only registered students can mark attendance!")

    if len(name_dict) == 0:
        st.warning("No faces registered yet! Please go to Register tab first!")
    else:
        att_image = st.camera_input("Take photo for Attendance", key="att")

        if att_image:
            file_bytes = np.asarray(bytearray(att_image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            faces, gray = detect_faces(img)

            if len(faces) == 0:
                st.error("No face detected!")
            else:
                # Load recognizer
                if not os.path.exists(MODEL_FILE):
                    train_model()

                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.read(MODEL_FILE)

                marked = False
                for (x,y,w,h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200,200))

                    id_, confidence = recognizer.predict(face_roi)

                    # Confidence < 70 means good match
                    if confidence < 70:
                        person_name = name_dict.get(str(id_), "Unknown")
                        # Draw box
                        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                        cv2.putText(img, f"{person_name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                        # Mark attendance
                        now = datetime.now()
                        date_str = now.strftime("%Y-%m-%d")
                        time_str = now.strftime("%H:%M:%S")

                        df_data = {"Name": [person_name], "Date": [date_str], "Time": [time_str], "Status": ["Present"]}

                        if os.path.exists(ATTENDANCE_FILE):
                            df_old = pd.read_csv(ATTENDANCE_FILE)
                            # Avoid duplicate same day
                            if not ((df_old['Name'] == person_name) & (df_old['Date'] == date_str)).any():
                                df_new = pd.concat([df_old, pd.DataFrame(df_data)], ignore_index=True)
                                df_new.to_csv(ATTENDANCE_FILE, index=False)
                                st.success(f"✅ Attendance Marked! Welcome {person_name}! Confidence: {100-confidence:.0f}%")
                            else:
                                st.info(f"ℹ️ {person_name}, your attendance already marked today!")
                        else:
                            pd.DataFrame(df_data).to_csv(ATTENDANCE_FILE, index=False)
                            st.success(f"✅ Attendance Marked! Welcome {person_name}!")

                        marked = True
                    else:
                        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
                        cv2.putText(img, "Unknown - Please Register", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
                        st.error("❌ Face Not Registered! Please go to Register tab first babe!")

                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=f"Found {len(faces)} face(s)")

with tab3:
    st.header("Attendance Records")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Excel/CSV", csv, "attendance.csv", "text/csv")

        if st.button("Clear All Attendance"):
            os.remove(ATTENDANCE_FILE)
            st.rerun()
    else:
        st.info("No attendance marked yet!")

    st.divider()
    st.subheader("Registered Students")
    if name_dict:
        st.write(list(name_dict.values()))
        if st.button("Clear All Registered Faces (Reset)"):
            for f in os.listdir("faces_data"):
                os.remove(os.path.join("faces_data", f))
            st.rerun()
    else:
        st.write("No students registered")
