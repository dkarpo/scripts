/*
  USB mouse emulation intended to act as a "keepalive" to prevent
  devices from sleeping. This is useful to keep Android phones (with
  an OTG cable) and computer systems awake if needed. This script
  requires an ATMega 32u4 based chip as those devices have native USB
  HID built in. A great device for this is the CJMCU Beetle which
  has a form factor that is half the size of a regular USB key and has
  a ATMega 32u4 chip on it.

  Reference documentation can be found at:
  
    https://www.arduino.cc/reference/en/language/functions/usb/mouse/

  Note: Do not set the mouseInterval *too* low or it will be tough to
  reprogram your device!

  Author: Derrick Karpo
  Date:   April 4, 2020
*/

#include <Mouse.h>

int ledState = LOW;             // default LED state (don't change)
const int ledPin =  13;         // internal LED pin (usually pin 13)
const int ledDelay =  500;      // LED hold delay of X ms
const int mouseInterval = 4000; // move the mouse every X ms


void setup() {
  Mouse.begin();
}

void ledwrite() {
  if (ledState == LOW) {
    ledState = HIGH;
  } else {
    ledState = LOW;
    delay(ledDelay);
  }
  digitalWrite(ledPin, ledState);
}

void loop() {
  ledwrite();                   // quickly turn the LED on
  Mouse.move(1, 0, 0);          // move the mouse slightly right
  ledwrite();                   // quickly turn the LED off
  Mouse.move(-1, 0, 0);         // move the mouse slightly left
  delay(mouseInterval);         // erm, sleepy time?
}
