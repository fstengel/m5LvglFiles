# No docstrings: this is microPython, and space comes at a premium
import lvgl as lv
import espidf

# from machine import Pin
from micropython import const

# I have not found it in espidf. Weird?
PCNT_PIN_NOT_USED = const(-1)

MAXSHORT = const(0x7FFF)
# Arbitrary. Just to brevent overflowing. Anythin less than MAXSHORT and large enough
MAXCOUNT = const(1000) 

# A class that uses the pulse counter to read an IO.
#
# PCNTButton(pinN, [unit]) : watches pin number pinN and uses PCNT unit unit. if unit==None,
# automatically allocates a PCNT unit.
#
# Methods:
# @property pressed: True iff the button is pressed
# getCount(): gets the count number. Zeroes it if abs(count)>=MAXCOUNT
# clearCount(): zeroes the counter.
#
# For the time being, the private methods/variables are not that private...
#
class PCNTButton(object):
    # I am unhappy with allocating pcnt units automagically.
    # I could use a lookup table with a singleton object ?
    currentUnit = espidf.PCNT_UNIT._0
    
    def __init__(self, pinN, unit = None):
        self._pinN = pinN
        # what argument name (if needed)? 
        self._filter = 1023
        if unit is None:
            self._allocatePCNT()
        else:
            self._unit = unit
        self._setupPCNT()
    
    def __repr__(self):
        return "PCNTButton({})".format(self._unit)
    
    def _allocatePCNT(self):
        if PCNTButton.currentUnit<espidf.PCNT_UNIT.MAX:
            self._unit = PCNTButton.currentUnit
            PCNTButton.currentUnit += 1
        else:
            raise ValueError("Too many counter units allocated...")
    
    def _setupPCNT(self):
        cntConfig = espidf.pcnt_config_t()
        cntConfig.channel = espidf.PCNT_CHANNEL._0
        cntConfig.pulse_gpio_num = self._pinN
        cntConfig.ctrl_gpio_num = PCNT_PIN_NOT_USED
        cntConfig.unit = self._unit
        cntConfig.pos_mode = espidf.PCNT_COUNT.INC
        cntConfig.neg_mode = espidf.PCNT_COUNT.INC
        cntConfig.lctrl_mode = espidf.PCNT_MODE.KEEP
        cntConfig.hctrl_mode = espidf.PCNT_MODE.KEEP
        cntConfig.counter_h_lim = MAXSHORT
        cntConfig.counter_l_lim = -MAXSHORT
        
        espidf.pcnt_filter_disable(self._unit)
        espidf.pcnt_set_filter_value(self._unit, self._filter)
        espidf.pcnt_filter_enable(self._unit)

        espidf.pcnt_unit_config(cntConfig)
        # useful ?
        espidf.pcnt_counter_pause(self._unit)
        espidf.pcnt_counter_clear(self._unit)
        espidf.pcnt_counter_resume(self._unit)
    
    def getCount(self):
        cnt_ptr = espidf.C_Pointer()
        espidf.pcnt_get_counter_value(self._unit, cnt_ptr)
        cnt = cnt_ptr.int_val
        if cnt>MAXCOUNT or cnt<-MAXCOUNT:
            self.clearCount()
        return cnt
    
    def clearCount(self):
        espidf.pcnt_counter_clear(self._unit)
    
    @property
    def pressed(self):
        cnt = self.getCount()
        return cnt%2==1

# Class creating a generic input device and associated driver
# This class is mainly virtual.
#
# BaseDevice([debug = False])
# creates a base input device. debug: flag for debugging.
#
# Methods:
# update(): needs to be overridden. Has to modify/update self._pressed, self._changed.
# @property pressed: if something is pressed.
# @property changed: something recently changed.
# _reader: the callback. Needs to be overridden.
# getReader(): returns the callback used to register the device.
#
# registerDriver(): registers ithe input device and returns the driver
# extraRegistration(): performs the extra thigns after registration. Needs to be overridden.
#    For buttons, this method would set up the points array etc.
# getDriver() : retrievec the driver after registering it if necessary.
#
# Only POINTERs do not make use of a group: I am adding the feature to the base class. Alhough It could do
# it with a derived class. Too cumbersome?
#
# @property group: the group associated with this device
# @group.setter: the setter for the group
#
# No points  (only BUTTONS make use of it...)
#
# In addition to overriding the various methods, one has to adapt the content of self._devType in __init__
# to reflect the actual device type.

class BaseDevice(object):
    def __init__(self, debug = False):
        self._debug = debug
        self._pressed = False
        self._changed = False
        if self._debug:
            print("basDevice Init. Attention: base class. Does (almost) nothing!")
        # for the inclusion of a driver
        self._devType = lv.INDEV_TYPE.NONE

# To override
    def update(self):
        pass
            
    @property
    def pressed(self):
        return self._pressed
    
    @property
    def changed(self):
        ch = self._changed
        self._changed = False
        return ch

# To override
    def _reader(self, drv, data):
        self.update()
        return False
    
    def getReader(self):
        return (lambda drv, data: self._reader(drv, data))
    
# To override
    def extraRegistration(self):
        pass
    
    def registerDriver(self):
        self._indev_drv = lv.indev_drv_t()
        lv.indev_drv_init(self._indev_drv)
        self._indev_drv.type = self._devType
        self._indev_drv.read_cb = self.getReader()
        self._driver = lv.indev_drv_register(self._indev_drv)
        self.extraRegistration()
        return self._driver
    
    def getDriver(self):
        if self._driver is None:
            self.registerDriver()
        return self._driver

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value
        if self._group is not None:
            lv.indev_set_group(self._driver, self._group)

# Class to drive the previous devices. Rather (too) general...
# To be removed: the registration is now be part of the device class...
#
# class deviceDriver(object):
#     def __init__(self, device, type):
#         self._type = type
#         self._device = device
#         self._indev_drv = lv.indev_drv_t()
#         lv.indev_drv_init(self._indev_drv)
#         self._indev_drv.type = self._type
#         self._indev_drv.read_cb = device.getReader()
#         self._driver = lv.indev_drv_register(self._indev_drv)
#         self._group=[]
#         if self._type==lv.INDEV_TYPE.KEYPAD:
#             pass
#         elif self._type==lv.INDEV_TYPE.ENCODER:
#             pass
#         elif self._type==lv.INDEV_TYPE.BUTTON:
#             lv.indev_set_button_points(self._driver, [pt0])
#         else:
#             # Not implemented. TBC
#             raise ValueError("Invalid/non implemented input device: {}".format(self._type))
#     
#     @property
#     def group(self):
#         return self._group
# 
#     @group.setter
#     def group(self, value):
#         self._group = value
#         if self._group is not None:
#             lv.indev_set_group(self._driver, self._group)
#     
#     def setPoints(self, pts):
#         self._points = pts
#         if self._points is None:
#             self._points = [pt0]
#         lv.indev_set_button_points(self._driver, self._points)
        
