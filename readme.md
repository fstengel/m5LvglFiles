# Basic input device library for an M5Stack with LittlevGL

## Prerequisites

An M5Stack with microPython+LittlevGL bindings. Beware I use the last version of the bindings for V6.x (there is a small diffrence with the prototype of `indev_set_button_points`).

See threads:

* https://forum.littlevgl.com/t/hardware-button-multiple-points/1953
* https://forum.littlevgl.com/t/error-lv-bindings-driver-generic-modlvindev-c/2016/15

TBD:

* write in a separate document a HOWTO build uPY+lvgl using the latest...

 
## Installation

The best way is to create a folder named `m5inputs` in the `/lib` folder (to be created if it does not exist) and copy files `__init__.py`, `base.py`, `m5encoder.py`, `keypad.py` and `m5buttons.py` (the contents of the `m5inputs` folder on github) in that folder.

## The search path

You may want to check if the package is in the search path. Check from REPL:

```Python
import sys
print(sys.path)
```

if `['', '/lib']` (or `['/lib', '']`) is printed then all is ok. If not, check in `boot.py` (or `main.py`) if `sys.path` is modified. If not, add a few lines to `boot.py` to the effect:

* the previous script printed `['']`. add the lines:
```Python
import sys
sys.path.append(['/lib'])
```
* the previous script printed `['/lib', '']`, then you may want to change the order:
```Python
import sys
sys.path[0]=''
sys.path[1]='/lib'
```
* the previous script printed nothing, then I am stumped. Something could be wrong with your microPython install...

The list `sys.path` contains the folders that will be explored by microPython to find a module. AFAIK `['', '/lib']` means first the current folder then `/lib`.

## Usage

```Python
from m5inputs.m5encoder import M5ButtonEncoder
from m5inputs.keypad  import KeyButton, Keypad
from m5inputs.m5buttons immport M5Buttons
from m5inputs.navkey import NavKey
```

See the `exKbd`, `exEnc`, `exBtn` and `exNav` (TBD) scripts for examples

## The `base` package

Contains classes `PCNTButton` and `BaseDevice`

### Class `PCNTButton`

A class that uses the pulse counter to read an IO. It only works by polling. No IRQ/ISR !

`PCNTButton(pinN, [unit = None])`: watches pin number `pinN` and uses PCNT unit `unit`. if `unit==None`,
automatically allocates a PCNT unit.

Methods:

* `@property pressed`: True iff the button is pressed
* `getCount()`: gets the count number. Zeroes it if abs(count)>=MAXCOUNT
* `clearCount()`: zeroes the counter.

For the time being, because of a hardware issue (Wifi sending spurious plusses to button A), the counter gets reset if its absolute value is above a harcoded constant (`MAXCOUNT = const(1000)`)

TBD:

* For the time being, the private methods/variables are not that private...


### Class `BaseDevice`

Class creating a generic input device and associated driver.
This class is mainly virtual.

`BaseDevice([debug = False])`: creates a base input device.

- `debug`: flag for debugging.

Methods:

* `update()`: *needs to be overridden*. Has to modify/update self._pressed, self._changed.
* `@property pressed`: if something is pressed.
* `@property changed`: something recently changed. Is reset after read.
* `_reader`: the callback. *Needs to be overridden*.
* `getReader()`: returns the callback used to register the device.

* `registerDriver()`: registers the input device and returns the driver
* `extraRegistration()`: performs the extra thigns after registration. *Needs to be overridden*.
For buttons, this method would set up the points array etc.
* `getDriver()`: retrieves the driver after registering it if necessary.

Only `POINTER`s do not make use of a group: I am adding the feature to the base class. Alhough It could do
it with a derived class. Too cumbersome?

* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group. Only has an effect *after* the driver has been registered.

No points  (only `BUTTON`s make use of it...)

In addition to overriding the various methods, one has to adapt the content of `self._devType` in `__init__`
to reflect the actual device type.

TBD.
* Render a few classes really private
* `update()` should reall be private...
* write a `@property` peekChanged: to see if chnged recently without resetting it

For an actual use case see the code for `M5ButtonEncoder` in the `m5encoder` package.

## The `keypad` package

Declares the `KeyButton` and `Keypad` classes.

## Class `KeyButton`

Class to simulate a key press using a physical button (aka DigitalInput). Beware, this can only be used for polling. No IRQ/ISR.

`KeyButton(pinN, [keyboard = None], [key = None], [unit = None], [debug = False])`: 
watches pin number `pinN` and sends `key` to `keyboard` if not `None`. `unit` is the PCNT
unit (if `None`, automatically allocated) and `debug` is a flag for debug messages.

Methods:

* `@property key`: the key code associated with the button.
* `@property pressed`: the key is pressed.

## Class `Keypad`

Class making a keyboard input device and driver

`Keypad([debug = False])`: creates a keyboard/keypad input device.

- `debug`: flag for debugging.

Methods:

* `addKey(key)`: adds the key KeyButton object to the keyboard
* `update()`: does the work. It scans the keys to find the first one that is pressed (if one is)
   and updates the various internal variables. Real crappy implementation.
* `@property currentKey`: the key code currently pressed (or the last pressed). Initally `0`.
* `@property pressed`: if the current key is pressed. Initially `False`.
* `@property changed`: something recently changed in the key: changed key. (de)Pressed key. Cleared to false after read
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group. Only has an effect *after* the driver has been registered.

See example: `exKbd`for a working example.

TBD:

* Composite keys

## The `m5encoder` package

Declares the `M5ButtonEncoder` class

### Class `M5ButtonEncoder`

Class making a encoder input device using the M5Stack's buttons as:

*   key A: decreases the encoder value
*   key B: presses the encoder
*   key C: increases the encoder value

`M5ButtonEncoder([step = 3], [debug = False])`:
creates a button encoder input device. `step`: number of times a key has to be seen by the reading loop in order to register as a move. This slows down the movement.

- `debug`: flag for debugging.

Methods:

* `update()`: does the work. Calculates the current difference and sees if anything has changed.
* `@property diff`: the diff sent by the encoder. The higher `step` is, the longer one has to press A/C to move.
* `@property pressed`: if the encoder key (key B) is pressed. Initially `False`.
* `@property changed`: something recently changed in encoder: a move, pressed
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group. Only has an effect *after* the driver has been registered.

See example: `exEnc` for a working example.

The `step` parameter controls how long one has to press button A/C in order to have the encoder register a diff. See exEnc and play with the step parameter.

TBD:

* setter/getter for the `step` parameter

## the `m5buttons` package

Declares the `M5Buttons` class. This is still a WIP

### Class `M5Buttons`

Class managing the buttons for the M5Stack. WIP.

`M5Buttons([debug = False])`: Creates a device+driver to manage the buttons of an M5Stack.

- `debug`: flag for... debugging.

Methods:

* `setLinkedButtons(btA, btB, btC)`: links the physical buttons and the logical objects. If button A is
pressed/released then `btA` recieves the corrsponding event through pressing/releasing in its center.
if the logical object is `None`, then point (0,0) will be acted upon.
* `setLinkeButton(btnId, bt)`: links physical button id `bntId` (0 for button A etc.) and object `bt`. Same idea as above.
* `update()`: does the work. Checks which button is pressed/released.
* `@property pressed`: if a button is pressed. Initially `False`
* `@property btn`: the id of the last button which changed state. Initially `0`.
* `@property changed`: something recently changed in encoder: a button is pressed or the button has changed
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group

See example `exBtn` for a working example.

TBD.

* Handle multiple presses/depresses. WIP.
* write a `@property` to get last button pressed/released (`@property btn`: possible name)

### Public items

Among others:

* Function `getCenter(obj)` that calculates the center of the lvgl  object `obj`. Returns a lvgl `point_t`. Could move to `base.py`
* `pt0` an lvgl `point_t` object initialized to point (0,0). Same as above.

## The navkey. WIP

It is in two classes: I2CNavKey in i2cnavkey and NavKey in navkey

### Class `I2CNavKey`

 Class that attempts to manage this navkey: [https://www.tindie.com/products/saimon/i2c-navkey-7-functions-joypad-on-the-i2c-bus](https://www.tindie.com/products/saimon/i2c-navkey-7-functions-joypad-on-the-i2c-bus)
 No IRQs or some such. Only polling...
 WIP!

 `I2CNavKey(i2c, [addr = navAddr], [debug=False])`: creates an object managing navkey at address `adr` on i2c bus `i2c`.
 
 * `i2c`: an I2C object describing the bus
 * `addr``: address of the navkey. By default `navAddr=CONST(0x10)`.`
 * `debug`: flag for... debugging.

Methods:
 
 * `resetNavkey()`: resets the navkey. sleeps for 400us in order to wait for the restart. TBD: add a flag to forego the sleep
 * `initNavKey()`: initializes/configures the navkey. Starts by resetting it... The encoder is set to wrap. TBD add a flags argument to enhance configuration.
 * `setEcoderBounds([min = -5], [max = 5], [step = 1])`: stets the minimum, maximum bound and the step for the encoder.
 * `updateStatus()`: reads the status registe and updates the various flags
 * `getStatus()`: updates the status and returns it  as a list of:
     - `True`: pressed,
	 - `False`: released,
	 - `None`: untouched since last poll.
 * `getEncoder()`: gets the encoder value as a signed integer
 * `keyEvent()`: gets the last key event as a tuple `(bool, obj)`. Two forms
    - `(False, None)`: if there was no new event,
	- `(True, (key, bool))` where `key` is the key code and `bool` is `True` iff the key is pressed.
 * `encoderEvent()`: gets the last encoder event as a tuple `(bool, obj)`. Two forms
     `(False, None)` if there was no new event,
     `(True, (nat, bool))` where nat is the code (either rotation or bounds touched) and `bool` is `True` depending on the nature (see datasheet).
 
 There are quite a few other internals dealing with i2c communication and reading/writing 1,2 or 4 bytes from/to a register.
 

### Class `NavKey` part of the `navkey`package
 
 part of the navkey package.

 Class that makes a I2CNavKey a hybrid input device in lvgl.
 WIP!

 `NavKey(i2c, [addr = navAddr], [debug=False])`: creates an object managing navkey at address `adr` on i2c bus `i2c`.
 
- `i2c`: an I2C object describing the bus
- `addr`: address of the navkey. By default `navAddr=CONST(0x10)`
- `debug`: flag for... debugging.

Methods:
 
* `update()`: does the work. Polls the i2c navkey, checks the keys, calculates the current difference and sees if anything has changed.
* `property diff`: the diff sent by the encoder. The higher step is, the longer one has to press A/C to move.
* `@property keyPressed`: if a key is pressed
* `@property pressed`: if the encoder key (key CTR) is pressed
* `@property keyChanged`: some key changed
* `@property encoderChanged`: something recently changed in encoder: a move, pressed
* `getKeyReader()`: returns the callback used to register the keys device. It is seen by lvgl as a keypad.
* `registerKeyDriver()`: registers the keypad device associated with the navkey
* `getKeyDriver()`: returns the registered keypad driver
* `getEncoderReader()`: returns the callback used to register the encoder device. It is sen by lvgl as an encoder.
* `registerEncoderDriver()`: registers the encoder device associated with the navkey
* `getEncoderDriver()`: returns the registered encoder driver
* `@property keyGroup`:
* `keyGroup.setter`: getter/setter for the group associated with the keypad device
* `@property encoderGroup`:
* `encoderGroup.setter`: getter/setter for the group associated with the encoder device

TBD

* a way to remap the keys on the fly. Possible interface: `setKey(navKey, lvglKeyCode)`. Almost hard coded for now
* find a way to have only the keypad or encoder to handle the CTR button.

## The examples

### `exBtn`, `exEnc` and `exKbd`

All based on the same script: four buttons labelled 1 to 4 on the top of the screen.

* `exEnc` and `exKbd` navigate these buttons using either the `Keypad` or the `M5ButtonEncoder` input devices
* `exBtn` toys with the first three buttons (just press/release)

The relevant bits of code are in the last dozen lines of code.

### `exNav`

TBD. Will show the use of the navkey...



