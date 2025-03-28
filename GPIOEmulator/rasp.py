import cv2
import numpy as np
import time
import threading
from datetime import datetime
import winsound

from EmulatorGUI import GPIO, App

BUZZER_PIN = 24

app = App()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

def control_buzzer():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def activate_buzzer():
    threading.Thread(target=winsound.Beep, args=(1000, 500), daemon=True).start()
    buzzer_thread = threading.Thread(target=control_buzzer, daemon=True).start()

camera = cv2.VideoCapture(0)
ret, frame1 = camera.read()
ret, frame2 = camera.read()
last_warning_time = 0

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
            threading.Thread(target=activate_buzzer, daemon=True).start()
            last_warning_time = current_time

    cv2.imshow("Security Camera", frame1)
    frame1 = frame2
    ret, frame2 = camera.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
GPIO.cleanup()