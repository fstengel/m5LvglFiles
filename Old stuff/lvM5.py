from ili9341 import ili9341

from micropython import const

BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)

class M5Ili(ili9341):
    def __init__(self, hybrid = True, double_buffer = False):
        self.disp = ili9341(miso=19, mosi=23, clk=18, cs=14, dc=27, rst=33, backlight=32,power=-1,power_on=-1, backlight_on=1,
                mhz=40, factor=4, hybrid=hybrid, width=320, height=240,
                colormode=ili9341.COLOR_MODE_BGR, rot=ili9341.MADCTL_ML, invert=False, double_buffer=double_buffer)

        