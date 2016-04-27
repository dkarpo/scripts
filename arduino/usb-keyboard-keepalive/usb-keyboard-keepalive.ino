/*
  USB Keyboard emulation intended to act as a "keepalive" to prevent
  devices from sleeping.  This is useful to keep Android phones (with
  an OTG cable) and computer systems awake if needed.  This script
  requires an ATMega 32u4 based chip as those devices have native USB
  HID built in.  A great  device for this is the CJMCU Beetle which
  has a form factor that is half the size of a regular USB key and has
  a ATMega 32u4 chip on it.

  Sample keyboard codes can be found at: 
    http://www.arduino.cc/en/Reference/KeyboardModifiers

  Note: Do not set the keyInterval *too* low or it will be tough to
  reprogram your device!

  Author: Derrick Karpo
  Date:   April 24, 2016
*/

#include <Keyboard.h>

int ledState = LOW;           // default LED state (don't change)
const int ledPin =  13;       // the number of the internal LED pin (usually pin 13)
const int keyWrite = 0x81;    // what keystroke to type (0x81 == Left-Shift)
const int keyInterval = 4000; // input the keystroke every X ms (don't set this too low!)


void setup() {
  pinMode(ledPin, OUTPUT);
  Keyboard.begin();
}

void ledwrite() {
  if (ledState == LOW) {
    ledState = HIGH;
  } else {
    ledState = LOW;
  }
  digitalWrite(ledPin, ledState);
}

void loop() {
  ledwrite();                 // quickly turn the LED on
  Keyboard.write(keyWrite);   // send a Left-Shift key
  ledwrite();                 // quickly turn the LED off
  delay(keyInterval);         // erm, sleepy time?
}
