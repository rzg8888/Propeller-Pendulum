#include<Servo.h>
Servo ESC;

float dt, last_time;
float integral, previous, output = 0;
float kp =5, ki = 0.9, kd = 0; // Ganancias del PID (ajústalas según sea necesario)
float setpoint = 45.00; // Valor deseado del ángulo
const int pinPotSP = A0;
const int pinPotP = A1;
const int pinPotI = A2;
const int pinPotD = A3;
const int pinPotAng = A4;

// Rango del ESC
const int ESC_MIN = 1050;
const int ESC_MAX = 2500;



float pid(float error) {
  float proportional = error;
  if (dt < 0.0001) dt = 0.0001;
  integral += error * dt;
  float derivative = (error - previous) / dt;
  previous = error;
  float output = (kp * proportional) + (ki * integral) + (kd * derivative);
  return output;
}

void setup() {
  ESC.attach(9);

  ESC.writeMicroseconds(1000);
  delay(5000); //Esperar 1.2 segundos para hacer la activacion
}

void loop() {
  Serial.begin(115200);
  int valorPotSP = analogRead(pinPotSP);
  int valorPotP = analogRead(pinPotP);
  int valorPotI = analogRead(pinPotI);
  int valorPotD = analogRead(pinPotD);
  int valorAng = analogRead(pinPotAng);
  setpoint = map(valorPotSP, 0, 1023, 0, 110);  
  kp = map(valorPotP, 0, 1023, 0, 300) / 1000.0;
  ki = map(valorPotI, 0, 1023, 0, 2000) / 100000.0;
  kd = map(valorPotD, 0, 1023, 0, 3000) / 10000.0;
  float actual = map(valorAng, 0, 1023, 0,270);
  float now = millis();
  dt = (now - last_time) / 1000.00;
  last_time = now;
  
  float error = setpoint - actual;
  output = pid(error);

  // Mapeo de la salida PID al rango del ESC
  int escOutput = map(output, 0, 65, ESC_MIN, ESC_MAX);
  
  ESC.writeMicroseconds(escOutput);

    Serial.print(setpoint);
    Serial.print(',');
    Serial.print(actual);
    Serial.print(',');
    Serial.print(output);
    Serial.print(',');
    Serial.print(kp);
    Serial.print(',');
    Serial.print(ki);
    Serial.print(',');
    Serial.println(kd);
    delay(50);
}