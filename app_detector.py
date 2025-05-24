import cv2
from datetime import datetime
import time
import os

# Buat folder log & screenshots jika belum ada
os.makedirs("screenshots", exist_ok=True)

# Load model deteksi wajah dari OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
'/haarcascade_frontalface_default.xml')
# Inisialisasi webcam
cap = cv2.VideoCapture(0)

# Timer untuk deteksi wajah hilang
last_seen = time.time()
face_missing_start = None

# Variabel untuk mencegah spam peringatan dan statistik
last_warning_time = 0
warning_cooldown = 3
total_violations = 0
multiple_face_count = 0
missing_face_count = 0

print("=== Sistem Deteksi Kecurangan Ujian Online ===")
print("Tekan 'q' untuk keluar")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_time = time.time()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Deteksi lebih dari satu wajah dengan cooldown
    if len(faces) > 1:
        if current_time - last_warning_time > warning_cooldown:
            msg = f"[{now}] PELANGGARAN: Terdeteksi {len(faces)} wajah!"
            print(msg)
            with open("cheating_log.txt", "a", encoding='utf-8') as log:
                log.write(msg + "\n")
            cv2.imwrite(f"screenshots/multiple_faces_{datetime.now().strftime('%H%M%S')}.jpg", frame)
            total_violations += 1
            multiple_face_count += 1
            last_warning_time = current_time
    
    # 2. Deteksi wajah menghilang
    if len(faces) == 0:
        if face_missing_start is None:
            face_missing_start = time.time()
        elif time.time() - face_missing_start > 3:
            missing_duration = current_time - face_missing_start
            msg = f"[{now}] PELANGGARAN: Wajah tidak terlihat selama {missing_duration:.1f} detik!"
            print(msg)
            with open("cheating_log.txt", "a", encoding='utf-8') as log:
                log.write(msg + "\n")
            cv2.imwrite(f"screenshots/no_face_{datetime.now().strftime('%H%M%S')}.jpg", frame)
            total_violations += 1
            missing_face_count += 1
            face_missing_start = None  # reset setelah log
    else:
        face_missing_start = None  # reset jika wajah terlihat
    
    # Tampilkan kotak wajah dengan warna sesuai kondisi
    for (x, y, w, h) in faces:
        if len(faces) == 1:
            color = (0, 255, 0)  # Hijau untuk normal
            status = "NORMAL"
        else:
            color = (0, 0, 255)  # Merah untuk mencurigakan
            status = "MENCURIGAKAN"
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, status, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Buat overlay untuk informasi status
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 90), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    info_lines = [
        f"Waktu: {datetime.now().strftime('%H:%M:%S')}",
        f"Wajah: {len(faces)} | Pelanggaran: {total_violations}"
    ]
    
    # Tampilkan countdown jika wajah hilang
    if face_missing_start is not None:
        missing_time = current_time - face_missing_start
        info_lines.append(f"Wajah Hilang: {missing_time:.1f}s")
    
    for i, line in enumerate(info_lines):
        cv2.putText(frame, line, (15, 30 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    cv2.imshow("Ujian Online - Deteksi Kecurangan", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n=== RINGKASAN ===")
print(f"Total Pelanggaran: {total_violations}")
print(f"Multiple Faces: {multiple_face_count}")
print(f"Missing Face: {missing_face_count}")