#!/usr/bin/python3
#
# A simple GUI clock in Python which shows the current time and timezone.
#
# Gratuitiously taken from http://stackoverflow.com/questions/15689667.
#
# Author: Derrick Karpo
# Date:   September 1, 2015
#

import re
import sys
from tkinter import Tk, Label, BOTH
import time

root = Tk()
root.title('System Date and Time')
root.resizable(0,0)
root.attributes("-topmost", 1)
time1 = ''
clock = Label(root, font=('courier', 16, 'bold'), bg='black', fg='red')
clock.pack(fill=BOTH, expand=1)


def tick():
    global time1
    # a hack to display the TZ in short form under Windows
    td = time.strftime('%Y%b%d %H:%M:%S')
    tz = time.strftime('%Z')
    display = ("%s %s") % (td, re.sub(r'[^A-Z]', '', tz))

    if td != time1:
        time1 = td
        clock.config(text=display)
    clock.after(1000, tick)


tick()
root.mainloop()
