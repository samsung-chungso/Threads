#include "Wire.h"
#include <MPU6050_light.h>

//칼만 계수 및 자이로
float kalman_y = 0.0;  // Estimated state (yaw)
float P_y = 1.0;       // Error covariance
float Q_y = 0.001;     // Process noise
float R_y = 0.03;      // Measurement noise

MPU6050 mpu(Wire);
unsigned long timer = 0;
unsigned long previousTime = 0;

//pid 요소
float Kp = 2.0;  // Proportional gain
float Ki = 0.0;  // Integral gain
float Kd = 1.0;  // Derivative gain

float setpoint = 9.0; // Desired yaw angle (0 degrees)
float integral = 0.0;
float previousError = 0.0;

// Motor control pins
const int motor1_Pin1 = 9;
const int motor1_Pin2 = 10;
const int motor2_Pin1 = 11;
const int motor2_Pin2 = 12;

const long interval =30;
unsigned long lastTime;
double elapsedTime;


void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  byte status = mpu.begin();
  Serial.print(F("MPU6050 status: "));
  Serial.println(status);
  while(status!=0){ } // stop everything if could not connect to MPU6050
  
  Serial.println(F("Calculating offsets, do not move MPU6050"));
  delay(1000);
  // mpu.upsideDownMounting = true; // uncomment this line if the MPU6050 is mounted upside-down
  mpu.calcOffsets(); // gyro and accelero
  Serial.println("Done!\n");

  pinMode(motor1_Pin1, OUTPUT);
  pinMode(motor1_Pin2, OUTPUT);
  pinMode(motor2_Pin1, OUTPUT);
  pinMode(motor2_Pin2, OUTPUT);

}

void loop() {
  unsigned long currentTime = millis();
  if((currentTime - previousTime) >= interval){ 
    mpu.update();
    float yaw = getFilteredYaw(mpu.getAngleY());
    Serial.println(yaw);
    float error = setpoint - yaw;  // Error between desired and current yaw
    elapsedTime = (double)(currentTime - lastTime) / 1000;
    integral += error * elapsedTime; // Integral term using 100ms interval
    
    float derivative = (error - previousError) / elapsedTime;  // Derivative term
    float correction = Kp * error + Ki * integral + Kd * derivative;  // PID output
    int motorOutput = (int)constrain(correction, -255, 255);
    setMotorPWM(motorOutput);
	  previousTime = currentTime;
  }

}

float getFilteredYaw(float raw_yaw) {
  // Kalman filter update
  P_y += Q_y;                              // Prediction update
  float K_y = P_y / (P_y + R_y);           // Compute Kalman gain
  kalman_y = kalman_y + K_y * (raw_yaw - kalman_y);  // Update estimate
  P_y = (1 - K_y) * P_y;                   // Update error covariance
  return kalman_y;
}
void setMotorPWM(int pwm) {
  if (pwm > 0) {
    analogWrite(motor1_Pin1, pwm);
    digitalWrite(motor1_Pin2, LOW);
    analogWrite(motor2_Pin1, pwm);
    digitalWrite(motor2_Pin2, LOW);
  } else {
    analogWrite(motor1_Pin2, -pwm);
    digitalWrite(motor1_Pin1, LOW);
    analogWrite(motor2_Pin2, -pwm);
    digitalWrite(motor2_Pin1, LOW);
  }
}
