import machine
import gc
import network
import lvgl as lv
#from m5_lvgl import ButtonsInputEncoder, EncoderInputDriver
#from lvInputsC import Keyboard, KeyButton, M5ButtonEncoder, deviceDriver
#from m5inputs.keypad  import KeyButton, Keypad
#from m5inputs.base import deviceDriver
from m5inputs.m5encoder import M5ButtonEncoder, deviceDriver

from ili9341 import ili9341
import gc
import utime

import micropython
micropython.alloc_emergency_exception_buf(100)

from micropython import const
from machine import Pin

BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)


AUTHENTICATED = False

OPTION1 = False
OPTION2 = False
OPTION3 = False
OPTION4 = False


def connect():
 
    ssid = "Maison-ORBI"
    password =  "08Franie@11Crabole=12Atrel"
 
    station = network.WLAN(network.STA_IF)
 
    if station.isconnected() == True:
        print("Already connected")
        return
 
    station.active(True)
    station.connect(ssid, password)
 
    while station.isconnected() == False:
        utime.sleep_ms(100)
        print(".", end="")
    print("")
 
    print("Connection successful")
    print(station.ifconfig())

disp = ili9341(miso=19, mosi=23, clk=18, cs=14, dc=27, rst=33, backlight=32,power=-1,power_on=-1, backlight_on=1,
        mhz=40, factor=4, hybrid=True, width=320, height=240,
        colormode=ili9341.COLOR_MODE_BGR, rot=ili9341.MADCTL_ML, invert=False, double_buffer=False
               ) # Create a display driver

connect()

def event_handler(obj, event):
    """
    Called when a button is released.
    Parameters
    ----------
    btn :
        The Button that triggered the event.
    event :
        The triggering event.
    """
    global OPTION1, OPTION2, OPTION3, OPTION4
    if event == lv.EVENT.RELEASED:
        print("Clicked: %s" % lv.list.get_btn_text(obj))
        if lv.list.get_btn_text(obj) == "Option1":
            
            OPTION1 = True
 
        elif lv.list.get_btn_text(obj) == "Option2":
            
            OPTION2 = True

        elif lv.list.get_btn_text(obj) == "Option3":

            OPTION3 = True
            
        elif lv.list.get_btn_text(obj) == "Option4":
            
            OPTION4 = True

screen = lv.obj()

# Keyboard/pad version
# kbd = Keypad(debug= True)
# kbdRead = kbd.getReader()
# tA = KeyButton(BUTTON_A_PIN, keyboard = kbd, key = lv.KEY.LEFT, debug= True)
# tB = KeyButton(BUTTON_B_PIN, keyboard = kbd, key = lv.KEY.ENTER, debug= True)
# tC = KeyButton(BUTTON_C_PIN, keyboard = kbd, key = lv.KEY.RIGHT, debug= True)
# driv = deviceDriver(kbd, lv.INDEV_TYPE.KEYPAD)

# ButtonEncoder version
enc = M5ButtonEncoder(debug = True)
# driv = deviceDriver(enc, lv.INDEV_TYPE.ENCODER)
driv = enc.registerDriver()


list1 = lv.list(screen)
AUTHENTICATED = True
if AUTHENTICATED:
    list1.set_size(300, 154)
    list1.align(None, lv.ALIGN.CENTER, 0, -5)   
    
            # Add buttons to the list

    list_btn = list1.add_btn(lv.SYMBOL.FILE, "Option1")
    list_btn.set_event_cb(event_handler)
    
    list_btn = list1.add_btn(lv.SYMBOL.DIRECTORY, "Option2")
    list_btn.set_event_cb(event_handler)
    
    list_btn = list1.add_btn(lv.SYMBOL.DIRECTORY, "Option3")
    list_btn.set_event_cb(event_handler)     
else:
    list1.set_size(300, 100)
    list1.align(None, lv.ALIGN.CENTER, 0, -5) 
    
            # Add buttons to the list
    list_btn = list1.add_btn(lv.SYMBOL.FILE, "Option2")
    list_btn.set_event_cb(event_handler)
    
    list_btn = list1.add_btn(lv.SYMBOL.DIRECTORY, "Option3")
    list_btn.set_event_cb(event_handler)
    
group = lv.group_create()
lv.group_add_obj(group, list1)
enc.group = group

lv.group_set_style_mod_cb(group, None)
lv.group_set_style_mod_edit_cb(group,None)
lv.group_set_editing(group, True)
   
lv.scr_load(screen)

