/*
  Bluetooth Low Energy (BLE) HID Keyboard using a nRF52 based
  board. It's intended to act as a "keepalive" to prevent devices from
  sleeping by sending a Left-Shift key every X seconds.  This is
  useful to keep Android or iOS phones and computer systems awake if
  needed. This script requires an nRF52 based board such as a Adafruit
  Feather nRF52 and is pretty much a rip-off of the hid_keyboard
  sample. :D

  Author: Derrick Karpo
  Date:   February 28, 2019
*/


#include <bluefruit.h>
#define ADV_TIMEOUT 500         // X seconds (0 = forever, always advertise)
int ledState = LOW;             // default LED state (don't change)
const int ledPin =  17;         // the number of the internal LED pin
const int keyInterval = 4000;   // input the keystroke every X ms (don't set this too low!)

BLEDis bledis;
BLEHidAdafruit blehid;


void setup() {
  // setup device with maximum output power
  Bluefruit.begin();
  Bluefruit.setTxPower(4);
  Bluefruit.setName("BLE nRF52 Keepalive");

  // start device information service
  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Feather nRF52");
  bledis.begin();

  // start BLE HID
  blehid.begin();

  // setup and start advertising
  startAdv();
}


void startAdv(void) {
  // advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addAppearance(BLE_APPEARANCE_HID_KEYBOARD);

  // include BLE HID service
  Bluefruit.Advertising.addService(blehid);

  // BLE HID setup
  Bluefruit.Advertising.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);      // in units of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);        // how long to stay in fast mode
  Bluefruit.Advertising.start(ADV_TIMEOUT);        // stop BLE advertising after X seconds
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


void loop() {
  ledwrite();                   // turn the LED on
  blehid.keyPress(0xE1);        // send Left-Shift key
  delay(100);                   // debounce
  blehid.keyRelease();          // release all keys
  ledwrite();                   // turn the LED off
  delay(keyInterval);           // erm, sleepy time?
}
