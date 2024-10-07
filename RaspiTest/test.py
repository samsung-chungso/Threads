import cv2

# 카메라 장치 번호를 지정합니다. 기본 웹캠은 0번입니다.
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    # 카메라에서 프레임을 읽어옵니다.
    ret, frame = cap.read()

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 프레임을 화면에 표시합니다.
    cv2.imshow('Camera', frame)

    # 'q' 키를 누르면 루프를 종료합니다.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라와 창을 닫습니다.
cap.release()
cv2.destroyAllWindows()
