import cv2
import os

# Create folder for your face images
if not os.path.exists('dataset'):
    os.makedirs('dataset')

cam = cv2.VideoCapture(0)
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Look at camera, collecting 50 photos...")
count = 0
name = input("Enter your name (e.g. Hasini): ")

while True:
    ret, frame = cam.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        count += 1
        # Save face image
        cv2.imwrite(f"dataset/{name}_{count}.jpg", gray[y:y+h, x:x+w])
        print(f"Collected {count}/50")
    
    cv2.imshow('Collecting Faces - Press q to stop', frame)
    
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    if count >= 50:
        break

cam.release()
cv2.destroyAllWindows()
print(f"Done! 50 images saved for {name}")