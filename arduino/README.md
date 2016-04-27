# arduino

This repository currently contains an Arduino sketch which can be used
to provide USB keyboard emulation via a ATMega 32u4 based device.  The
programmed device will act as a "keepalive" to prevent devices from
sleeping.  This is useful to keep Android phones (with an OTG cable)
and computer systems awake if needed.   The script requires an ATMega
32u4 based chip as those devices have native USB HID built in.  A
great device for this is the CJMCU Beetle which has a form factor that
is half the size of a regular USB key and has a ATMega 32u4 chip on
it.
