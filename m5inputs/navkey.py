from .base import BaseDevice
import lvgl as lv

from micropython import const
from machine import I2C, Pin
import utime
import ustruct

from i2cnavkey import I2CNavKey, triVal, navAddr, UP, DN, LT, RT, CTR, MAXMIN

MIN = 0
MAX = 15
STEP = 1
MOD = MAX-MIN+1

# Hardcoded for now.
keyDict = {UP: lv.KEY.UP, DN: lv.KEY.DOWN, LT: lv.KEY.LEFT, RT: lv.KEY.RIGHT, CTR: lv.KEY.ENTER}

# Class that makes a I2CNavKey a hybrid inout device in lvgl.
# WIP!
#
# NavKey(i2c, [addr = navAddr], [debug=False])
# creates an object managing navkey at address adr on i2c bus i2c.
# i2c: an I2C object describing the bus
# addr: address of the navkey. By default navAddr=CONST(0x10)
# debug: flag for... debugging.
#
# Methods:
# update(): does the work. Polls the i2c navkey, checks the keys, calculates the current difference and sees if anything has changed.
# @property diff: the diff sent by the encoder. The higher step is, the longer one has to press A/C to move.
# @property keyPressed: if a key is pressed
# @property pressed: if the encoder key (key CTR) is pressed
# @property keyChanged: some key changed
# @property encoderChanged: something recently changed in encoder: a move, pressed
# getKeyReader(): returns the callback used to register the keys device. It is seen by lvgl as a keypad.
# registerKeyDriver(): registers the keypad device associated with the navkey
# getKeyDriver(): returns the registered keypad driver
# getEncoderReader(): returns the callback used to register the encoder device. It is sen by lvgl as an encoder.
# registerEncoderDriver(): registers the encoder device associated with the navkey
# getEncoderDriver(): returns the registered encoder driver
# @property keyGroup:
# keyGroup.setter: getter/setter for the group associated with the keypad device
# @property encoderGroup:
# encoderGroup.setter: getter/setter for the group associated with the encoder device
#

# Should not really be derived from Base device: only pressed is used !
class NavKey(BaseDevice):
    def __init__(self, i2c, addr = navAddr, debug = False):
        self._i2c = i2c
        self._addr = addr
        self._debug = debug
        self._pressed = False
        self._keyPressed = False
        self._keyChanged = False
        self._encChanged = False
        self._key = 0
        self._enc = 0
        self._diff = 0
        self._nav = I2CNavKey(i2c, addr, debug)
        self._nav.setEncoderBounds(MIN, MAX, STEP)
        self._encDriver = None
        self._keyDriver = None
    
    def update(self):
        st = self._nav.getStatus()
        ke = self._nav.keyEvent()
        ee = self._nav.encoderEvent()
        # Logic to evolve
        # One might want to add flags to tell what to do with the centre key
        # is that key sending an encoder event, key event or both?
        # For the time beign, it is hardcoded as both...
        if ke[0]:
            ev = ke[1]
            if self._key!=ev[0] or self._keyPressed!=ev[1]:
                if ev[0]==CTR:
                    self._pressed = ev[1]
                self._keyChanged = True
                self._key = ev[0]
                self._keyPressed = ev[1]
        if ee[0]:
            ev = ee[1]
            enc = self._nav.getEncoder()
            d = 0
            if enc != self._enc:
                d = enc-self._enc
                if st[MAXMIN] is True:
                    d += MOD
                elif st[MAXMIN] is False:
                    d -= MOD
            self._diff = d
            self._enc = enc
            self.encChanged = (d!=0)
    
    @property
    def diff(self):
        di = self._diff
        self._diff = 0
        return di
    
    @property
    def keyPressed(self):
        return self._keyPressed
    
    @property
    def keyChanged(self):
        ch = self._keyChanged
        self._keyChanged = False
        return ch
                
    @property
    def encoderChanged(self):
        ch = self._encChanged
        self._encChanged = False
        return ch
    
    def _keyReader(self, drv, data):
        self.update()
        data.key = keyDict[self._key]
        if self.keyPressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.keyChanged:
            print("Key reader: [{}] key: {}, state: {}".format(self, data.key, data.state))
        return False
    
    def _encReader(self, drv, data):
        self.update()
        data.enc_diff = self.diff
        if self.pressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.encoderChanged:
            print("Encoder reader : [{}] diff: {} enc: {}, state: {}".format(self, data.enc_diff, self._enc, data.state))
        return False
        
    def getKeyReader(self):
        return (lambda drv, data: self._keyReader(drv, data))
        
    def getEncoderReader(self):
        return (lambda drv, data: self._encReader(drv, data))
        
    def registerKeyDriver(self):
        self._keydev_drv = lv.indev_drv_t()
        lv.indev_drv_init(self._keydev_drv)
        self._keydev_drv.type = lv.INDEV_TYPE.KEYPAD
        self._keydev_drv.read_cb = self.getKeyReader()
        self._keyDriver = lv.indev_drv_register(self._keydev_drv)
        return self._keyDriver
    
    def getKeyDriver(self):
        if self._keyDriver is None:
            self.registerKeyDriver()
        return self._keyDriver

    def registerEncoderDriver(self):
        self._encdev_drv = lv.indev_drv_t()
        lv.indev_drv_init(self._encdev_drv)
        self._encdev_drv.type = lv.INDEV_TYPE.ENCODER
        self._encdev_drv.read_cb = self.getEncoderReader()
        self._encDriver = lv.indev_drv_register(self._encdev_drv)
        return self._keyDriver
    
    def getEncoderDriver(self):
        if self._encDriver is None:
            self.registerEncoderDriver()
        return self._encDriver

    @property
    def keyGroup(self):
        return self._keyGroup

    @keyGroup.setter
    def keyGroup(self, value):
        self._keyGroup = value
        if self._keyGroup is not None:
            lv.indev_set_group(self._keyDriver, self._keyGroup)

    @property
    def encoderGroup(self):
        return self._encGroup

    @encoderGroup.setter
    def encoderGroup(self, value):
        self._encGroup = value
        if self._encGroup is not None:
            lv.indev_set_group(self._encDriver, self._encGroup)

    
                
            

   
