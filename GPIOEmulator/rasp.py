import cv2
import numpy as np
import time
import threading
from datetime import datetime
import sys
from EmulatorGUI import GPIO, App  # Giả sử file thư viện tên là GPIO.py

# Định nghĩa chân GPIO
BUZZER_PIN = 24  # GPIO24 cho buzzer

# Khởi tạo GUI GPIO
app = App()

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

# Hàm kích hoạt buzzer
def activate_buzzer():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Bật buzzer
    time.sleep(0.5)  # Giữ trong 0.5 giây
    GPIO.output(BUZZER_PIN, GPIO.LOW)   # Tắt buzzer

# Khởi tạo camera và các biến
camera = cv2.VideoCapture(0)
ret, frame1 = camera.read()
ret, frame2 = camera.read()
last_warning_time = 0

# Vòng lặp chính
while camera.isOpened():
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if any(cv2.contourArea(contour) > 500 for contour in contours):
        current_time = time.time()
        if current_time - last_warning_time >= 1:
            warning_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⚠️ WARNING: Movement detected at {warning_time}")
            threading.Thread(target=activate_buzzer, daemon=True).start()  # Kích hoạt buzzer trong luồng riêng
            last_warning_time = current_time

    cv2.imshow("Security Camera", frame1)
    frame1 = frame2
    ret, frame2 = camera.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
camera.release()
cv2.destroyAllWindows()
GPIO.cleanup()