#include <Servo.h>

Servo servoMotor;

const int ledPin1 = 8;  // Green light
const int ledPin2 = 11; // Red light


void setup() {
  // put your setup code here, to run once:

  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);

  // Initially red light
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);

}

void loop() {

  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);
  // put your main code here, to run repeatedly:

}
