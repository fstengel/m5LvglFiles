# Basic input device library for an M5Stack with LittlevGL

## Installation

The best way is to create a folder named `m5inputs` in the `/lib` folder (to be created if it does not exist) and copy files `__init__.py`, `m5encoder.py`, `keypad.py` and `m5buttons.py` in that folder.

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

`from m5inputs.m5encoder import M5ButtonEncoder`
`from m5inputs.keypad  import KeyButton, Keypad`
`from m5inputs.m5buttons immport M5Buttons`

See the `exKbd`, `exEnc` and `exBtn` scripts for examples

## The `base` package

Contains classes `PCNTButton` and `BaseDevice`

### Class `PCNTButton`

A class that uses the pulse counter to read an IO. It only works by polling. No IRQ/ISR !

* `PCNTButton(pinN, [unit = None])`: watches pin number `pinN` and uses PCNT unit `unit`. if `unit==None`,
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

* `BaseDevice([debug = False])`: creates a base input device. `debug`: flag for debugging.

Methods:

* `update()`: *needs to be overridden*. Has to modify/update self._pressed, self._changed.
* `@property pressed`: if something is pressed.
* `@property changed`: something recently changed.
* `_reader`: the callback. *Needs to be overridden*.
* `getReader()`: returns the callback used to register the device.

* `registerDriver()`: registers the input device and returns the driver
* `extraRegistration()`: performs the extra thigns after registration. *Needs to be overridden*.
For buttons, this method would set up the points array etc.
* `getDriver()`: retrieves the driver after registering it if necessary.

Only `POINTER`s do not make use of a group: I am adding the feature to the base class. Alhough It could do
it with a derived class. Too cumbersome?

* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group

No points  (only `BUTTON`s make use of it...)

In addition to overriding the various methods, one has to adapt the content of `self._devType` in `__init__`
to reflect the actual device type.

TBD.
* Render a few classes really private
* `update()` should reall be private...

For an actual use case see the code for `M5ButtonEncoder` in the `m5encoder` package.

## The `keypad` package

Declares the `KeyButton` and `Keypad` classes.

## Class `KeyButton`

Class to simulate a key press using a physical button (aka DigitalInput). Beware, this can only be used for polling. No IRQ/ISR.

* `KeyButton(pinN, [keyboard = None], [key = None], [unit = None], [debug = False])`: 
watches pin number `pinN` and sends `key` to `keyboard` if not `None`. `unit` is the PCNT
unit (if `None`, automatically allocated) and `debug` is a flag for debug messages.

Methods:

* `@property key`: the key code associated with the button.
* `@property pressed`: the key is pressed.

## Class `Keypad`

Class making a keyboard input device and driver

`Keypad([debug = False])`: creates a keyboard/keypad input device. `debug`: flag for debugging.

Methods:

* `addKey(key)`: adds the key KeyButton object to the keyboard
* `update()`: does the work. It scans the keys to find the first one that is pressed (if one is)
   and updates the various internal variables. Real crappy implementation.
* `@property currentKey`: the key code currently pressed (or the last pressed)
* `@property pressed`: if the current key is pressed
* `@property changed`: something recently changed in the key: changed key. (de)Pressed key. Cleared to false after read
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group

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
`debug`: flag for debugging.

Methods:

* `update()`: does the work. Calculates the current difference and sees if anything has changed.
* `@property diff`: the diff sent by the encoder. The higher `step` is, the longer one has to press A/C to move.
* `@property pressed`: if the encoder key (key B) is pressed
* `@property changed`: something recently changed in encoder: a move, pressed
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group

See example: `exEnc` for a working example.

TBD:

* setter/getter for the `step` parameter

## the `m5buttons` package

Declares the `M5Buttons` class. This is still a WIP

### Class `M5Buttons`

Class managing the buttons for the M5Stack. WIP.

`M5Buttons([debug = False])`: Creates a device+driver to manage the buttons of an M5Stack. `debug`: flag for... debugging.

Methods:

* `setLinkedButtons(btA, btB, btC)`: links the physical buttons and the logical objects. If button A is
pressed/released then `btA` recieves the corrsponding event through pressing/releasing in its center.
if the logical object is `None`, then point (0,0) will be acted upon.
* `setLinkeButton(btnId, bt)`: links physical button id `bntId` (0 for button A etc.) and object `bt`. Same idea as above.
* `update()`: does the work. Calculates the current difference and sees if anything has changed.
* `@property pressed`: if a button is pressed
* `@property changed`: something recently changed in encoder: a button is pressed or the button has changed
* `getReader()`: returns the callback used to register the device.
* `registerDriver()`: registers the input device and returns the driver
* `getDriver()`: retrieves the driver after registering it if necessary.
* `@property group`: the group associated with this device
* `@group.setter`: the setter for the group

See example `exBtn` for a working example.

TBD.

* Handle multiple presses/depresses.

### Pubilc items

Among others:

* Function `getCenter(obj)` that calculates the center of the lvgl  object `obj`. Returns a lvgl `point_t`.
* `pt0` an lvgl `point_t` object initialized to point (0,0).

## The examples

### `exBtn`, `exEnc` and `exKbd`

All based on the same script: four buttons labelled 1 to 4 on the top of the screen.

* `exEnc` and `exKbd` navigate these buttons using either the `Keypad` or the `M5ButtonEncoder` input devices
* `exBtn` toys with the first three buttons (just press/release)

The relevant bits of code are in the last dozen lines of code.



