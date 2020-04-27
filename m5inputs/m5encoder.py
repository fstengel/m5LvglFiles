from .base import PCNTButton, BaseDevice
import lvgl as lv

from micropython import const

# M5Stack button pins
BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)

# Class making a encoder input device using the M5Stack's buttons as:
#    -, previous, left, down: key A
#    enter: key B
#    +, next, right, up: key C
#
# M5ButtonEncoder([step = 3], [debug = False])
# creates a button encoder input device. step: number of times a key has to be seen by the reading loop in order to register as a move.
# debug: flag for debugging.
#
# Methods:
# update(): does the work. Calculates the current difference and sees if anything has changed.
# @property diff: the diff sent by the encoder. The higher step is, the longer one has to press A/C to move.
# @property pressed: if the encoder key (key B) is pressed
# @property changed: something recently changed in encoder: a move, pressed
# getReader(): returns the callback used to register the device.
#
class M5ButtonEncoder(BaseDevice):
    def __init__(self, step = 3, debug = False):
        self._debug = debug
        self.btA = PCNTButton(BUTTON_A_PIN)
        self.btB = PCNTButton(BUTTON_B_PIN)
        self.btC = PCNTButton(BUTTON_C_PIN)
        self._changed = False
        self._pressed = False
        self._step = step
        self._diff = 0
        self._devType = lv.INDEV_TYPE.ENCODER
        self._group = []
    
    # Override
    def update(self):
        d = 0
        f = True
        if self.btA.pressed:
            d -= 1
            f = False
        if self.btC.pressed:
            d += 1
            f = False
        self._diff += d
        if f:
            self._diff = 0
        if d!=0:
            self._changed = True
        if self._pressed!=self.btB.pressed:
            self._changed = True
        self._pressed = self.btB.pressed
        
        
    @property
    def diff(self):
        # // behaves mathematicaly, so we have to take care of the sign...
        di = self._diff
        if di>0:
            d = di//self._step
        else:
            d = -(-di//self._step)
        if d!=0:
            self._diff = 0
            return d
        else:
            return 0
    
    # Override
    def _reader(self, drv, data):
        self.update()
        data.enc_diff = self.diff
        if self.pressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.changed:
            print("Encoder reader : [{}] diff: {} (actual: {}), state: {}".format(self, data.enc_diff, self._diff, data.state))
        return False

# To be removed
#     @property
#     def group(self):
#         return self._group
# 
#     @group.setter
#     def group(self, value):
#         self._group = value
#         if self._group is not None:
#             lv.indev_set_group(self._driver, self._group)
    