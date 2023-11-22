#include <Servo.h>

Servo servoMotor;

const int ledPin1 = 8;  // Green light
const int ledPin2 = 11; // Red light
const int servoPin = 10;

bool gateOpened = false;

void setup() {
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);

  servoMotor.attach(servoPin);
  servoMotor.write(0);  // Initialize servo position

  // Initially red light
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);
}

void rotateservo(int angle) {
  angle = constrain(angle, 0, 180);  // Ensure the angle is within the valid range
  servoMotor.write(angle);
  delay(15);
}

void openGate() {
  digitalWrite(ledPin1, HIGH);
  digitalWrite(ledPin2, LOW);

  for (int i = 0; i <= 90; i++) {
    rotateservo(i);
  }

  delay(4000); // Wait for 4 seconds

  for (int i = 90; i >= 0; i--) {
    rotateservo(i);
  }

  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);
}

void loop() {
  // Your resident comparison logic here
  // For simplicity, let's assume a variable named isResident is set based on the comparison
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);
  delay(2000);
  bool isResident = true;  // Replace with your actual logic

  if (isResident && !gateOpened) {
    openGate();
    gateOpened = true;  // Set the flag to true to indicate that the gate has been opened
    // Add any additional logic or actions you want to perform after opening the gate
  } else if (!isResident && gateOpened) {
    // Reset the flag when no resident is detected
    gateOpened = false;
  }

  // Your other non-blocking loop logic here
}