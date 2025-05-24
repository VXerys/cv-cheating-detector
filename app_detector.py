import cv2
from datetime import datetime
import time
import os

os.makedirs("screenshots", exist_ok=True)

# Load model deteksi wajah dari OpenCV menggunakan Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inisialisasi webcam (kamera default adalah 0)
cap = cv2.VideoCapture(0)

# Variabel untuk tracking waktu dan kondisi
face_missing_start = None  # Kapan wajah mulai hilang
last_warning_time = 0      # Timer untuk mencegah spam peringatan yang sama
warning_cooldown = 3       # Jeda 3 detik antara peringatan yang sama

# Counter untuk statistik sederhana
total_violations = 0
multiple_face_count = 0
missing_face_count = 0

print("=== Aplikasi Deteksi Kecurangan Ujian Online ===")
print("Sistem akan memantau dua kondisi mencurigakan:")
print("1. Lebih dari satu wajah dalam frame")
print("2. Wajah tidak terlihat lebih dari 3 detik")
print("Tekan 'q' untuk keluar")
print("-" * 50)

while True:
    # Baca frame dari webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Tidak dapat membaca dari webcam")
        break
    
    # Dapatkan waktu saat ini
    current_time = time.time()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Konversi frame ke grayscale untuk mempercepat proses deteksi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Deteksi wajah dalam frame
    # Parameter: scaleFactor untuk memperkecil gambar, minNeighbors untuk akurasi
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    # Jika terdeteksi lebih dari 1 wajah, kemungkinan ada orang lain yang membantu
    if len(faces) > 1:
        # Gunakan cooldown untuk mencegah spam peringatan
        if current_time - last_warning_time > warning_cooldown:
            violation_msg = f"[{now}] PELANGGARAN: Terdeteksi {len(faces)} wajah!"
            print(violation_msg)
            
            # Simpan ke file log
            with open("cheating_log.txt", "a", encoding='utf-8') as log_file:
                log_file.write(violation_msg + "\n")
            
            # Ambil screenshot sebagai bukti
            screenshot_name = f"screenshots/multiple_faces_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(screenshot_name, frame)
            print(f"Screenshot disimpan: {screenshot_name}")
            
            # Update counter dan timer
            total_violations += 1
            multiple_face_count += 1
            last_warning_time = current_time
    
    # Jika tidak ada wajah terdeteksi
    if len(faces) == 0:
        # Mulai timer jika ini pertama kali wajah hilang
        if face_missing_start is None:
            face_missing_start = current_time
        
        # Cek apakah wajah sudah hilang lebih dari 3 detik
        missing_duration = current_time - face_missing_start
        if missing_duration > 3:
            violation_msg = f"[{now}] PELANGGARAN: Wajah tidak terlihat selama {missing_duration:.1f} detik!"
            print(violation_msg)
            
            # Simpan ke file log
            with open("cheating_log.txt", "a", encoding='utf-8') as log_file:
                log_file.write(violation_msg + "\n")
            
            # Ambil screenshot kondisi tidak ada wajah
            screenshot_name = f"screenshots/no_face_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(screenshot_name, frame)
            print(f"Screenshot disimpan: {screenshot_name}")
            
            # Update counter dan reset timer
            total_violations += 1
            missing_face_count += 1
            face_missing_start = None  # Reset timer setelah peringatan
    else:
        # Reset timer jika wajah terlihat kembali
        face_missing_start = None
    
    # Gambar kotak di sekitar setiap wajah yang terdeteksi
    for (x, y, w, h) in faces:
        # Tentukan warna kotak berdasarkan jumlah wajah
        if len(faces) == 1:
            color = (0, 255, 0)  # Hijau untuk kondisi normal
            status_text = "NORMAL"
        else:
            color = (0, 0, 255)  # Merah untuk kondisi mencurigakan
            status_text = "MENCURIGAKAN"
        
        # Gambar rectangle di sekitar wajah
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Tambahkan label status di atas kotak
        cv2.putText(frame, status_text, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Buat background gelap untuk teks agar mudah dibaca
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (450, 90), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Tampilkan informasi status di layar
    info_lines = [
        f"Waktu: {datetime.now().strftime('%H:%M:%S')}",
        f"Wajah Terdeteksi: {len(faces)}",
        f"Total Pelanggaran: {total_violations}"
    ]
    
    # Jika wajah sedang hilang, tampilkan countdown
    if face_missing_start is not None:
        missing_time = current_time - face_missing_start
        info_lines.append(f"Wajah Hilang: {missing_time:.1f} detik")
    
    # Gambar setiap baris informasi
    for i, line in enumerate(info_lines):
        y_position = 30 + (i * 20)
        cv2.putText(frame, line, (15, y_position),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    # Tampilkan frame dengan semua overlay
    cv2.imshow("Sistem Monitoring Ujian - Deteksi Kecurangan", frame)
    
    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\n" + "="*50)
print("RINGKASAN MONITORING SELESAI")
print("="*50)
print(f"Total Pelanggaran: {total_violations}")
print(f"- Multiple Faces: {multiple_face_count}")
print(f"- Missing Face: {missing_face_count}")
print("File log: 'cheating_log.txt'")
print("Screenshots: folder 'screenshots/'")
print("="*50)