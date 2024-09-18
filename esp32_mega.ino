  #include "BluetoothSerial.h"  // BluetoothSerial 라이브러리 포함

BluetoothSerial SerialBT;     // BluetoothSerial 객체 생성
char incomingChar;
void setup() {
  Serial.begin(115200);       // ESP32의 시리얼 모니터 설정
  SerialBT.begin("ESP32_BT"); // 블루투스 장치 이름 설정 (ESP32_BT로 설정)
  Serial.println("Bluetooth device is ready to pair");
}

void loop() {
  // 핸드폰에서 블루투스로 데이터를 수신하면 처리
  if (SerialBT.available()>0) {
    incomingChar = SerialBT.read();  // 블루투스로 받은 데이터 읽기
    Serial.print("Received: ");
    Serial.println(incomingChar);         // 수신한 데이터 시리얼 모니터에 출력

    // 여기서 받은 데이터를 기반으로 원하는 동작 수행 (예: 모터 제어, LED 켜기 등)
    // 예시: 만약 'F'를 받으면 앞으로 전진
    if (incomingChar == 'a') {
      Serial.println("Moving forward");
      // 여기에 전진 코드 추가
    }
    // 'B'를 받으면 후진
    else if (incomingChar == '0') {
      Serial.println("stop");
      // 여기에 후진 코드 추가
    }
  }
    // if (incomingChar == 'a') {
    //   Serial.println("Moving forward");
    //   // 여기에 전진 코드 추가
    // }
    // // 'B'를 받으면 후진
    // else if (incomingChar == '0') {
    //   Serial.println("stop");
    //   // 여기에 후진 코드 추가
    // }
}
