#include <SoftwareSerial.h>

// Using SoftwareSerial for debugging
SoftwareSerial Serial2(7, 8);

const int encoderPin = 2;
const int motorPin1 = 9;
const int motorPin2 = 10;
volatile int pulseCount = 0;
unsigned long previousMillis = 0;
const long interval = 100;
const int pulsesPerRevolution = 20;
const int referenceRpm = 500;

float Kp = 0.2;  // 비례 계수

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
  Serial2.println("Start...");
  pinMode(encoderPin, INPUT_PULLUP);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(encoderPin), countPulse, RISING);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    int rpm = (pulseCount * 60) / pulsesPerRevolution;
    pulseCount = 0;

    // P 제어기 계산
    int error = referenceRpm - rpm;
    float output = Kp * error;

    // 모터 속도 조절
    int motorSpeed = constrain(output, 0, 255);
    analogWrite(motorPin1, motorSpeed);
    digitalWrite(motorPin2, LOW);

    Serial.println(rpm);
    // 데이터 전송
    byte data_buffer[6] = {0};
    data_buffer[0] = 0xf5; // Start byte
    data_buffer[1] = 4;    // Length byte (4 bytes for RPM)
    data_buffer[2] = (rpm >> 24) & 0xff;
    data_buffer[3] = (rpm >> 16) & 0xff;
    data_buffer[4] = (rpm >> 8) & 0xff;
    data_buffer[5] = rpm & 0xff;

    // Serial.write(data_buffer, 6); // Send the packet
  }
}

void countPulse() {
  pulseCount++;
}