from machine import I2C, Pin
from micropython import const
import utime

import ustruct

# The base address of the navkey : no soldered pads.
navAddr = const(0x10)

# registers
# Just a selection of now !
rGConf = const(0x0)
rIStatus = const(0x06)
rCVal = const(0x0A)
rCMax = const(0x0E)
rCMin = const(0x12)
rIStep = const(0x16)

# flags for GConf
fDType = const(0b1<<0)
fWrapE = const(0b1<<1)
fDirE = const(0b1<<2)
# 3 others ignored for now...
fReset = const(0b1<<7)

# flags for IStatus
fUPR = const(0b1<<0)
fUPP = const(0b1<<1)
fDNR = const(0b1<<2)
fDNP = const(0b1<<3)
fRTR = const(0b1<<4)
fRTP = const(0b1<<5)
fLTR = const(0b1<<6)
fLTP = const(0b1<<7)
fCTRR = const(0b1<<8)
fCTRP = const(0b1<<9)
fCTRDP = const(0b1<<10)
fRInc = const(0b1<<11)
fRDec = const(0b1<<12)
fRMax = const(0b1<<13)
fRMin = const(0b1<<14)

UP = const(0)
DN = const(1)
LT = const(2)
RT = const(3)
CTR = const(4)
CTRD = const(5)
ROT = const(6)
MAXMIN = const(7)
MAXSTATES = const(8)



def triVal(pr, re):
    if pr:
        return True
    elif re:
        return False
    else:
        return None

# Class that attempts to manage this navkey: https://www.tindie.com/products/saimon/i2c-navkey-7-functions-joypad-on-the-i2c-bus
# No IRQs or some sutch. Only polling...
# WIP!
#
# I2CNavKey(i2c, [addr = navAddr], [debug=False])
# creates an object managing navkey at address adr on i2c bus i2c.
# i2c: an I2C object describing the bus
# addr: address of the navkey. By default navAddr=CONST(0x10)
# debug: flag for... debugging.
#
# Methods:
# resetNavkey(): resets the navkey. sleeps for 400us in order to wait for the restart. TBD: add a flag to forego the sleep
# initNavKey(): initializes the navkey. Starts by resetting it... The encoder is set to wrap.
# setEcoderBounds([min = -5], [max = 5], [step = 1]): stets the minimum, maximum bound and the step for the encoder.
# updateStatus(): reads the status registe and updates the various flags
# getStatus(): updates the status and returns it  as a list of:
#     True (pressed), False (released), None (untouched since last poll)
# getEncoder(): gets the encoder value as a signed integer
# keyEvent(): gets the last key event as a tuple (bool, obj). Two forms
#     (False, None) if there was no new event,
#     (True, (key, bool)) where key is the key code and bool is True iff the key is pressed.
# encoderEvent(): gets the last encoder event as a tuple (bool, obj). Two forms
#     (False, None) if there was no new event,
#     (True, (nat, bool)) where nat is the code (either rotation or bounds touched) and bool is True depending on the nature (see datasheet).
# 
# There are quite a few other internals dealing with i2c communication and reading/writing 1,2 or 4 bytes from/to a register.


class I2CNavKey(object):
    def __init__(self, i2c, addr = navAddr, debug = False):
        self._i2c = i2c
        self._addr = addr
        self._debug = debug
        self._buf1 = bytearray(1)
        self._buf2 = bytearray(2)
        self._buf4 = bytearray(4)
        self._status = [None]*MAXSTATES

        self.initNavKey()
        self.setEncoderBounds(min = 0, max = 15, step = 1)
        self._enc = 0
    

    def read1(self, dev, mem):
        self._i2c.readfrom_mem_into(dev, mem, self._buf1)
        return self._buf1[0]

    def write1(self, dev, mem, byte):
        self._buf1[0] = byte
        self._i2c.writeto_mem(dev, mem, self._buf1)

    def read2(self, dev, mem):
        self._i2c.readfrom_mem_into(dev, mem, self._buf2)
        a = ustruct.unpack(">H", self._buf2)
        return a[0]

    def write2(self, dev, mem, word):
        ustruct.pack_into(">H", self._buf2, 0, word)
        self._i2c.writeto_mem(dev, mem, self._buf2)

    def read4(self, dev, mem):
        self._i2c.readfrom_mem_into(dev, mem, self._buf4)
        a = ustruct.unpack(">i", self._buf4)
        return a[0]

    def write4(self, dev, mem, word):
        ustruct.pack_into(">i", self._buf4, 0, word)
        self._i2c.writeto_mem(dev, mem, self._buf4)

    def resetNavKey(self):
        # Reset the navKey
        self.write1(self._addr, rGConf, fReset)
        # A reset takes 400us.
        utime.sleep_us(400)

    def initNavKey(self):
        self.resetNavKey()
        # Should I have another choice ?
        # Wrap and increase in counter-trig direction
        self.write1(self._addr, rGConf, fWrapE)

    def setEncoderBounds(self, min = -5, max = 5, step = 1):
        self._minEnc = min
        self._maxEnc = max
        self._stepEnc = step
        self._mod = max-min+1
        self.write4(self._addr, rCMax, self._maxEnc)
        self.write4(self._addr, rCMin, self._minEnc)
        self.write4(self._addr, rIStep, self._stepEnc)
       
  
    def updateStatus(self):
        fl = self.read2(self._addr, rIStatus)
        self._status[UP] = triVal(fl&fUPP, fl&fUPR)
        self._status[DN] = triVal(fl&fDNP, fl&fDNR)
        self._status[LT] = triVal(fl&fLTP, fl&fLTR)
        self._status[RT] = triVal(fl&fRTP, fl&fRTR)
        self._status[CTR] = triVal(fl&fCTRP, fl&fCTRR)
        self._status[CTRD] = triVal(fl&fCTRDP, 0)
        self._status[ROT] = triVal(fl&fRInc, fl&fRDec)
        self._status[MAXMIN] = triVal(fl&fRMax, fl&fRMin)
    
    def getStatus(self):
        self.updateStatus()
        return self._status
    
    def getEncoder(self):
        a = self.read4(self._addr, rCVal)
        self._enc = a
        return a
    
    def keyEvent(self):
        for k in [UP, DN, LT, RT, CTR, CTRD]:
            st = self._status[k]
            if st is not None:
                return (True, (k, st)) 
        return (False, None)
    
    def encoderEvent(self):
        for k in [ROT, MAXMIN]:
            st = self._status[k]
            if st is not None:
                return (True, (k, st)) 
        return (False, None)
        
#     def getEncoder(self):
#         a = self.read4(self._addr, rCVal)
#         self._enc = a
#         return a
