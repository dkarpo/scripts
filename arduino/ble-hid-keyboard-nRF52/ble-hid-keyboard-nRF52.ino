/*
  Bluetooth Low Energy (BLE) HID Keyboard using a nRF52 based board.

  I'm using this with an Adafruit Feather nRF52 Bluefruit LE to act as
  a wireless pedal based teleprompt controller to "Page Up", "Page
  Down", and "Home" a laptop, tablet, or phone screen with lyrics
  during band jams. You can use it to create a wireless Bluetooth
  keyboard to press shortcut keys, as a volume control, to trigger
  screenshots, etc.

  The below code sends these keycodes when the physical buttons
  connected to pins 7, 15, or 16 are pressed. This code is a rip-off
  of the excellent samples from Adafruit! :D If you want to add more
  buttons and functions to other pins just modify the pins[] and
  hidcode[] array and wire some normally open (NO) momentary push
  buttons between the appropropriate digital pins and ground. I didn't
  add any debounce stuff because it doesn't seem like it needs it
  right now.

  As configured, once powered on, the HID device will beacon for 5
  minutes as "PedalPrompter" and you can pair your device to it with
  no pairing code required.

  Author: Derrick Karpo
  Date:   February 23, 2019
*/


#include <bluefruit.h>
#define ADV_TIMEOUT   500       // X seconds (0 = forever, always advertise)

BLEDis bledis;
BLEHidAdafruit blehid;

// digital pins and keycodes (see BLEHidGeneric.h)
uint8_t pins[]    = {7, 15, 16};
uint8_t hidcode[] = {HID_KEY_PAGE_UP, HID_KEY_PAGE_DOWN, HID_KEY_HOME};
uint8_t pincount  = sizeof(pins)/sizeof(pins[0]);
bool keyPressedPreviously = false;


void setup() {
  // setup device with maximum output power
  Bluefruit.begin();
  Bluefruit.setTxPower(4);
  Bluefruit.setName("PedalPrompter");

  // start device information service
  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Feather nRF52");
  bledis.begin();

  // set up defined pins as input (using the built-in pullup resistor)
  for (uint8_t i=0; i<pincount; i++) {
    pinMode(pins[i], INPUT_PULLUP);
  }

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


void loop() {
  bool anyKeyPressed = false;

  uint8_t modifier = 0;
  uint8_t count=0;
  uint8_t keycode[6] = {0};

  // scan normal key and send report
  for (uint8_t i=0; i < pincount; i++) {
    if (0 == digitalRead(pins[i])) {
      // if pin is active (low) add its HID code to the report
      keycode[count++] = hidcode[i];
      // max of 6 keycodes per report, then reset
      if (count == 6) {
        blehid.keyboardReport(modifier, keycode);
        count = 0;
        memset(keycode, 0, 6);
      }

      // used to trigger the all-zero report
      anyKeyPressed = true;
      keyPressedPreviously = true;
    }
  }

  // send any remaining keys (not accumulated up to 6)
  if (count) {
    blehid.keyboardReport(modifier, keycode);
  }

  // send all-zero report to indicate there are no keys pressed
  if (! anyKeyPressed && keyPressedPreviously) {
    keyPressedPreviously = false;
    blehid.keyRelease();
  }

  // poll interval
  delay(10);

  // request CPU to enter low-power mode until an event/interrupt occurs
  waitForEvent();
}
