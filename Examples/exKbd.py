# File: exKbd.py
# An example using the keypad device.
#
from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf(150)

import lvgl as lv

from m5inputs.keypad  import KeyButton, Keypad

from ili9341 import ili9341

disp = ili9341(miso=19, mosi=23, clk=18, cs=14, dc=27, rst=33, backlight=32,power=-1,power_on=-1, backlight_on=1,
        mhz=40, factor=4, hybrid=True, width=320, height=240,
        colormode=ili9341.COLOR_MODE_BGR, rot=ili9341.MADCTL_ML, invert=False, double_buffer=False
               ) # Create a display driver

# here one can add a wifi connection script to see if there is a wifi interaction
# import wifiConnect

# A screen with four buttons...
scr = lv.obj()

btn1 = lv.btn(scr)
lb1 = lv.label(btn1)
lb1.set_text("1")
btn1.set_size(60,40)
btn1.align(None, lv.ALIGN.IN_TOP_LEFT, 10, 10)

btn2 = lv.btn(scr)
lb2 = lv.label(btn2)
lb2.set_text("2")
btn2.set_size(60,40)
btn2.align(btn1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
# 
btn3 = lv.btn(scr)
lb3 = lv.label(btn3)
lb3.set_text("3")
btn3.set_size(60,40)
btn3.align(btn2, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
# 
btn4 = lv.btn(scr)
lb4 = lv.label(btn4)
lb4.set_text("4")
btn4.set_size(60,40)
btn4.align(btn3, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)

lv.scr_load(scr)

# M5Stack button pins
BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)

# The keypad
# I set debug to True: I want to see what is happening.
kbd = Keypad(debug= True)
tA = KeyButton(BUTTON_A_PIN, keyboard = kbd, key = lv.KEY.PREV, debug= True)
tB = KeyButton(BUTTON_B_PIN, keyboard = kbd, key = lv.KEY.ENTER, debug= True)
tC = KeyButton(BUTTON_C_PIN, keyboard = kbd, key = lv.KEY.NEXT, debug= True)

# register the device driver:

kbd.registerDriver()

# Create a group
group = lv.group_create()
lv.group_add_obj(group, btn1)
lv.group_add_obj(group, btn2)
lv.group_add_obj(group, btn3)
lv.group_add_obj(group, btn4)

# add it: only possible after registering the driver...
kbd.group = group

print("Setup finished...")
