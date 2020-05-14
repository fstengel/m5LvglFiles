from .base import PCNTButton, BaseDevice
import lvgl as lv

# Class to simulate a key press using a physical button (aka DigitalInput)
#
# KeyButton(pinN, [keyboard = None], [key = None], [unit = None], [debug = False])
# watches pin number pinN and sends key to keyboard if not None. unit is the PCNT
# unit (if None, autoatically allocated) and debug is a flag for debug messages.
#
# Methods:
# @property key: the key code associated with the button.
# @property pressed: the key is pressed.
#
class KeyButton(object):
    def __init__(self, pinN, keyboard = None, key = None, unit = None, debug = False):
        self._pressed = False
        self._changed = False
        self._debug = debug
        self.data = None
        self._keyboard = keyboard
        if self._keyboard:
            self._keyboard.addKey(self)
        self._cntB = PCNTButton(pinN, unit)
        self._key = key
        if self._debug:
            print("KeyButton Init {}".format(pinN))
    
    @property
    def key(self):
        return self._key
    
    @property
    def pressed(self):
        self._pressed = self._cntB.pressed
        return self._pressed
    

# Class making a keyboard input device
#
# Keypad([debug = False])
# creates a keyboard/keypad input device. debug: flag for debugging.
#
# Methods:
# addKey(key): adds the key KeyButton object to the keyboard
# update(): does the work. It scans the keys to find the first one that is pressed (if one is)
#    and updates the various internal variables. Real crappy implementation/name.
# @property currentKey: the key code currently pressed (or the last pressed)
# @property pressed: if the current key is pressed
# @property changed: something recently changed in the key: changed key. (de)Pressed key. Cleared to false after read
# getReader(): returns the callback used to register the device.
class Keypad(BaseDevice):
    def __init__(self, debug = False):
        self._key = 0
        self._pKey = None
        self._pressed = False
        self._debug = debug
        self._changed = False
        self._devType = lv.INDEV_TYPE.KEYPAD
        self._keys = []
        if self._debug:
            print("Keyboard Init")

    def addKey(self, key):
        (self._keys).append(key)
    
    # Override
    def update(self):
        if self._pressed:
            # I should not assume a physical key exists !
            if self._pKey is not None and self._pKey.pressed:
                self._pressed = True
                self._changed = False
            else:
                self._changed = True
                self._pressed = False
        else:
            for k in self._keys:
                if k.pressed:
                    self._changed = True
                    self._key = k.key
                    self._pKey = k
                    self._pressed = True
            
            
    @property
    def currentKey(self):
        return self._key

    # Override
    def _reader(self, drv, data):
        self.update()
        data.key = self.currentKey
        if self.pressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.changed:
            print("Key reader: [{}] key: {}, state: {}".format(self, data.key, data.state))
        return False
    
