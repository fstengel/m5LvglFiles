import lvgl as lv

from micropython import alloc_emergency_exception_buf
from machine import Pin

import lvInputs
from lvM5 import *


m5Ili = M5Ili()
disp = m5Ili.disp

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

# I set debug to True: I want to see what is happening.
kbd = lvInputs.Keyboard(debug= True)
kbdRead = kbd.getKeyboardReader()
tA = lvInputs.KeyButton(Pin(BUTTON_A_PIN), keyboard = kbd, key = lv.KEY.PREV, debug= True)
tB = lvInputs.KeyButton(Pin(BUTTON_B_PIN), keyboard = kbd, key = lv.KEY.ENTER, debug= True)
tC = lvInputs.KeyButton(Pin(BUTTON_C_PIN), keyboard = kbd, key = lv.KEY.NEXT, debug= True)

# create and register the keyboard input device
indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv)
indev_drv.type = lv.INDEV_TYPE.KEYPAD
indev_drv.read_cb = kbdRead
kbd_indev = lv.indev_drv_register(indev_drv)

# Create a group
group = lv.group_create()
lv.group_add_obj(group, btn1)
lv.group_add_obj(group, btn2)
lv.group_add_obj(group, btn3)
lv.group_add_obj(group, btn4)
# add it to the keyboard input device
lv.indev_set_group(kbd_indev, group)
