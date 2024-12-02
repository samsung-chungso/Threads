#include "BluetoothSerial.h"

// UART1 사용 설정 (핀 16: RX, 핀 17: TX)

BluetoothSerial SerialBT;  // BluetoothSerial 객체 생성

void setup() {
  Serial.begin(115200);            // ESP32 시리얼 모니터용
  Serial1.begin(9600, SERIAL_8N1, 16, 17);  // UART1 설정 (Mega와 통신)
  SerialBT.begin("ESP32_BT");      // 블루투스 장치 이름 설정
  Serial.println("Bluetooth device is ready to pair");
}

void loop() {
  // 블루투스에서 데이터를 수신하면 Mega로 전송
  if (SerialBT.available()) {
    char incomingChar = SerialBT.read();
    Serial1.write(incomingChar);   // Mega로 데이터 전송
    Serial.print("Sent to Mega: ");
    Serial.println(incomingChar);  // 시리얼 모니터에 전송된 데이터 출력
  }

  // Mega로부터 데이터를 수신하면 시리얼 모니터에 출력
  if (Serial1.available()) {
    char incomingChar = Serial1.read();
    Serial.print("Received from Mega: ");
    Serial.println(incomingChar);  // Mega에서 받은 데이터 출력
  }
}
