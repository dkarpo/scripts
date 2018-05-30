# arduino

This repository currently contains Arduino sketches which can be used
to provide Bluetooth, Bluetooth Low Energy (BLE), or USB keyboard emulation
via a ATMega 32u4 based device.  The programmed device acts as a "keepalive"
to prevent devices from sleeping.  This is useful to keep Android phones (via
an OTG cable), iOS devices, Windows devices, etc. awake if needed.
