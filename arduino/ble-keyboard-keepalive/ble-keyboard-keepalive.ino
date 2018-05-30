
/*
  Bluetooth Keyboard emulation intented to act as a "keepalive" to prevent devices from sleeping.  This
  is useful to keep Android or iOS phones and computer systems awake if needed.  This script requires
  an ATMega 32u4 based chip + Bluetooth module to perform keyboard emulation.  A great device for this
  is the Adafruit Feather 32u4.  This code is pretty much a rip-off of the hidkeyboard sample. :D

  Sample keyboard codes can be found at: http://www.arduino.cc/en/Reference/KeyboardModifiers

  Note: Do not set the keyInterval *too* low or it will be tough to reprogram your device!

  Author: Derrick Karpo
  Date:   May 26, 2018
*/

#include <Arduino.h>
#include <SPI.h>
#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "BluefruitConfig.h"
#if SOFTWARE_SERIAL_AVAILABLE
  #include <SoftwareSerial.h>
#endif

// variables
int ledState = LOW;                          // default LED state (don't change)
const int ledPin =  13;                      // the number of the internal LED pin (usually pin 13)
const char keyWrite[] = "02-00-00-00-00-00"; // what key(s) to type (Left-Shift)
const char keyRelease[] = "00-00";           // command to release the keys
const int keyInterval = 4000;                // input the keystroke every X ms (don't set this too low!)
const int factoryResetEnable = 0;            // should we factory reset for sanity?

// create the BLE object
Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

// error helper that outputs to the serial output, any error stops execution
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}

// flip the build in LED on or off
void ledwrite() {
  if (ledState == LOW) {
    ledState = HIGH;
  } else {
    ledState = LOW;
  }
  digitalWrite(ledPin, ledState);
}

// setup for the Bluetooth LE
void setup(void) {
  // make sure you can see the BLE device
  if (! ble.begin(VERBOSE_MODE)) {
    error(F("Could not find Bluetooth hardware."));
  }

  // perform a factory reset to make sure everything is in a known state
  if (factoryResetEnable) {
    if (! ble.factoryReset()) {
      error(F("Couldn't factory reset"));
    }
  }

  // set the device name
  if (! ble.sendCommandCheckOK(F("AT+GAPDEVNAME=BLE Keepalive"))) {
    error(F("Could not set device name?"));
  }

  // enable the HID service
  if (! ble.sendCommandCheckOK(F("AT+BLEHIDEN=On"))) {
    error(F("Could not enable Keyboard"));
  }

  // soft restart required after turning on HID mode
  if (! ble.reset()) {
    error(F("Failed to reset the BLE hardware."));
  }
}

// loop 
void loop(void) {
  ledwrite();                       // turn the LED on
  ble.print("AT+BLEKEYBOARDCODE="); // send Left-Shift key
  ble.println(keyWrite);            //
  delay(100);                       // debounce
  ble.print("AT+BLEKEYBOARDCODE="); // release all keys
  ble.println(keyRelease);          //
  ledwrite();                       // turn the LED off
  delay(keyInterval);               // erm, slesepy time?
}

