#include "Wire.h"
#include <MPU6050_light.h>

MPU6050 mpu(Wire);
unsigned long timer = 0;

float kalman_y = 0.0;  // Estimated state (yaw)
float P_y = 1.0;       // Error covariance
float Q_y = 0.001;     // Process noise
float R_y = 0.03;      // Measurement noise

float Kp = 1.0;  // Proportional gain
float Ki = 0.0;  // Integral gain
float Kd = 0.0;  // Derivative gain

void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  byte status = mpu.begin();
  Serial.print(F("MPU6050 status: "));
  Serial.println(status);
  while(status != 0) { } // stop everything if could not connect to MPU6050
  
  Serial.println(F("Calculating offsets, do not move MPU6050"));
  delay(1000);
  mpu.calcOffsets(); // gyro and accelero
  Serial.println("Done!\n");
}

void loop() {
  mpu.update();
  
  if((millis() - timer) > 10) { // print data every 10ms
    float x = mpu.getAngleY();
    float x_fil = getFilteredYaw(x);
    
    // Yaw 값을 시리얼로 전송
    sendYaw(x_fil);  // 필터링된 Yaw 값을 전송
    
    // PID 값 업데이트 (시리얼 수신)
    if (Serial.available()) {
      String receivedData = Serial.readStringUntil('\n');  // \n 까지 데이터를 읽음
      sscanf(receivedData.c_str(), "%f %f %f", &Kp, &Ki, &Kd);  // P, I, D 값 파싱
      Serial.print("New PID values: ");
      Serial.print(Kp); Serial.print(", ");
      Serial.print(Ki); Serial.print(", ");
      Serial.println(Kd);
    }

    timer = millis();
  }
}

float getFilteredYaw(float raw_yaw) {
  // Kalman filter update
  P_y += Q_y;  // Prediction update
  float K_y = P_y / (P_y + R_y);  // Compute Kalman gain
  kalman_y = kalman_y + K_y * (raw_yaw - kalman_y);  // Update estimate
  P_y = (1 - K_y) * P_y;  // Update error covariance
  return kalman_y;
}

void sendYaw(float yaw) {
  byte* byteYaw = (byte*)(void*)&yaw;  // float을 바이트 배열로 변환

  Serial.write(0xf5);  // Start byte
  Serial.write(0x04);  // Length byte (float는 4바이트)
  Serial.write(byteYaw, 4);  // float의 4바이트 전송
}