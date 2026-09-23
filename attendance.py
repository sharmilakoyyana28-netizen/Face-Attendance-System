import cv2, os, csv
import numpy as np
from datetime import datetime

print("Training faces... please wait")
dataset_path = 'dataset'
faces, names = [], []
label_map, current_id = {}, 0

for file in os.listdir(dataset_path):
    if file.endswith('.jpg'):
        name = file.split('_')[0]
        if name not in label_map:
            label_map[name] = current_id
            current_id += 1
        img_path = os.path.join(dataset_path, file)
        gray_img = cv2.imread(img_path, 0)
        faces.append(gray_img)
        names.append(label_map[name])

print(f"Found {len(faces)} images for {label_map}")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(names))
recognizer.save('trainer.yml')
print("Training Done!")

id_to_name = {v:k for k,v in label_map.items()}
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

if not os.path.exists('Attendance.csv'):
    with open('Attendance.csv', 'w', newline='') as f:
        csv.writer(f).writerow(['Name','Date','Time'])

marked = set()
print("Starting camera... look at camera. Press q to quit")

while True:
    ret, frame = cam.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_d = face_detector.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces_d:
        roi = cv2.resize(gray[y:y+h, x:x+w], (200,200))
        id_pred, conf = recognizer.predict(roi)
        if conf < 85:
            name = id_to_name[id_pred]
            acc = round(100-conf)
            if name not in marked:
                now = datetime.now()
                with open('Attendance.csv','a',newline='') as f:
                    csv.writer(f).writerow([name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])
                marked.add(name)
                print(f"Marked {name}")
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,f"{name} {acc}%",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        else:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.putText(frame,"Unknown",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    cv2.imshow('Face Attendance - Press q to exit', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cam.release()
cv2.destroyAllWindows()
print("Done! Check Attendance.csv")