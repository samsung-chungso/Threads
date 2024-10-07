import cv2
import os 
from tensorflow.keras.models import load_model
import numpy as np
import serial
import time
import threading

# 시리얼 포트 설정
port = '/dev/ttyUSB0'  # 사용하는 시리얼 포트 이름 변경 필요
baudrate = 9600  # 보드레이트 설정
timeout = 1  # 타임아웃 설정 (초 단위)
ser = serial.Serial(port, baudrate, timeout=timeout)
count = 0
def receive_serial():
    while True:
        if ser.inWaiting():
            command = ser.readline()
            cmd_dec = command.decode()
            print(cmd_dec)
            time.sleep(0.05)
task = threading.Thread(target = receive_serial)
task.start()

cap = cv2.VideoCapture(0)

class_labels = ["left", "right"]
model = load_model("vgg_arrow.h5")
#img = cv2.imread("dogs_53.png")

# index 값을 초기화
index = None

while True:
    ret, img = cap.read()

    if ret:
        img_scaled = cv2.resize(img, (64, 64), interpolation=cv2.INTER_AREA)
        data = img_scaled.astype("float")/255.0  # [[[0.896, ] [   ]...]]]

        X= np.asarray([data]) # [[[[0.896, ] [   ]...]]]]

        s = model(X, training=False)

        # 예측값이 0.5 이하인 경우 기본 메시지를 전송
        if np.max(s) <= 0.5:
            message = 'a30b\n'
        else:
            # 예측값이 0.5보다 큰 경우, 해당 클래스를 선택
            index = np.argmax(s)
            message = f'a{index}b\n'

        print(message)
        ser.write(message.encode('utf-8'))

        # 화면에 예측 결과 표시
        strr = class_labels[np.argmax(s)]
        cv2.putText(img, strr, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        cv2.imshow('win', img)
        # 시리얼 포트 닫기
        time.sleep(0.05)
        if cv2.waitKey(1)&0xff == ord('q'):
            break
    else:
        time.sleep(0.03)

# 종료 후 모든 창 닫기
cap.release()
cv2.destroyAllWindows()
ser.close()  # 시리얼 포트 닫기
