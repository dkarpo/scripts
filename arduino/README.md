# arduino

This repository currently contains Arduino sketches which can be used
to provide Bluetooth, Bluetooth Low Energy (BLE), or USB keyboard emulation
via ATMega 32u4 and nRF52  based devices. ie:

 * "keepalive" programmed devices prevent devices from sleeping.  This is useful to keep Android phones (via an OTG cable), iOS devices, Windows devices, etc. awake if needed.
 * "HID" programmed devices allow to you emulate a Bluetooth keyboard and use physical buttons (ie. via a foot pedal) to send any keypresses you require.
