import lvgl as lv
import machine
from machine import Pin
import utime

# Here L = 8
#mask = const(0b11111111)
#zero = const(0b00000000)
# Here L = 4 : flakier ?
mask = const(0b1111)
zero = const(0b0000)
#
# Debounce timeout : 2ms. Short, long, dunno?
# To be redesigned to stop WDT from tripping...
timeout = const(2000)

# For the time being all debug is done by printing...

# DigitalInput
# class to perform I/O from pin while debouncing it.
# As it is supposed to be a button, I suppose pin.value()==0 is the pushed (True) state
#
class DigitalInput(object):
    # the callback has signature: callback(pin, state)
    def __init__(self, pin, callback=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, debounce = True, debug = False):
        self._register = bytearray([mask])
        self._current_state = False
        self._previous_state = False
        self._pin = pin
        self._pin.init(mode=Pin.IN)
        self.setCallback(callback)
        self._debounce = debounce
        self._debug = debug
        #self._pin.init(self._pin.IN, trigger=trigger, handler=self._callback)
    
    def setCallback(self, callback=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING):
        self._user_callback = callback
        if callback is not None:
            self._pin.irq(handler=self._callback, trigger=trigger)
        else :
            self._pin.irq(handler=None)

    def _callback(self, pin):
        irq_state = machine.disable_irq()

        if self._debounce:
            t0 = utime.ticks_us()
            while True:
                t1 = utime.ticks_us()
                dt = utime.ticks_diff(t1,t0)
                if dt>timeout:
                    if self._debug:
                        print("Timeout !")
                    break
                
                self._register[0] <<= 1
                self._register[0] |= pin.value()

                #print("{:08b}".format(self._register[0]))
                # All bits set, button has been released for L loops
                if self._register[0] is mask:
                    self._current_state = False
                    break

                # All bits unset, button has been pressed for L loops
                if self._register[0] is zero:
                    self._current_state = True
                    break
        else:
            self._current_state = (self._pin.value()==0)

        # Handle edge case of two consequent rising interrupts
        if self._current_state is not self._previous_state:
            self._previous_state = self._current_state
            if self._user_callback is not None:
                self._user_callback(self._pin, self._current_state)

        machine.enable_irq(irq_state)

# Class to simulate a key press using a physical button (aka DigitalInput)
class KeyButton(object):
    def __init__(self, pin, keyboard = None, key = None, debug = False):
        self._press = False
        self._changed = False
        self._debug = debug
        self.setPin(pin)
        self.data = None
        self._keyboard = keyboard
        self._key = key
    
    def _cb(self, pin, press):
        if self._press != press:
            if self._debug:
                print("State change [{}] {}->{}".format(pin, self._press, press))
            self._changed = True
            self._press = press
            self.sendKey()
    
    def sendKey(self):
        if self._keyboard is not None:
            (self._keyboard).keyAction(self._key, self.pressed)
                
    
    @property
    def pressed(self):
        if self._debug:
            print("Coherent state: {}".format(self._press==(self._pin.value()==0)))
        return self._press
    
    @property
    def changed(self):
        ch = self._changed
        self._changed = False
        return ch
    
    def setPin(self, pin):
        # DigitalIput : the class that monitors/debounces pin
        self._pin = pin
        self._input = DigitalInput(pin, self._cb)

# Class making a keyboard input driver
class Keyboard(object):
    def __init__(self, debug = False):
        self._key = 0
        self._press = False
        self._debug = debug
        self._changed = False
    
    def keyAction(self, key, press):
        if key != self._key or press != self._press:
            self._changed = True
            if self._debug:
                print("Keyboard action [{}] {}: {}".format(self, key, press))
        self._key = key
        self._press = press
    
    @property
    def currentKey(self):
        key = self._key
        # Return to None?
        # self._key = None
        return key
    
    @property
    def changed(self):
        ch = self._changed
        self._changed = False
        return ch

    @property
    def pressed(self):
        return self._press
    
    def _reader(self, drv, data):
        data.key = self.currentKey
        if self.pressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.changed:
            print("Key reader : [{}] {}: {}".format(self, data.key, data.state))
        return False
    
    # The function that is the callback used to "read" the data from the keyboard
    def getKeyboardReader(self):
        return (lambda drv, data: self._reader(drv, data))

