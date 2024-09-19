void setup() {
  Serial.begin(115200);       // 시리얼 모니터와의 통신 속도 설정
  Serial1.begin(9600);        // ESP32와의 하드웨어 시리얼 통신 (TX1, RX1 핀 사용)
}

void loop() {
  // ESP32로부터 데이터를 수신하고 시리얼 모니터에 출력
  if (Serial1.available()) {
    char data = Serial1.read();    // ESP32로부터 데이터 수신
    Serial.print("Received from ESP32: ");
    Serial.println(data);          // 받은 데이터를 시리얼 모니터에 출력
  }

  // 시리얼 모니터에서 입력된 데이터를 ESP32로 전송

}