from .base import PCNTButton, BaseDevice
import lvgl as lv

from micropython import const

# M5Stack button pins
BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)

pt0 = lv.point_t()
pt0.x = 0
pt0.y = 0

def getCenter(obj):
    ar = lv.area_t()
    obj.get_coords(ar)
    pt = lv.point_t()
    pt.x = (ar.x1+ar.x2)//2
    pt.y = (ar.y1+ar.y2)//2
    return pt

# Class managing the buttons for the M5Stack
# WIP
#
# M5Buttons([debug = False])
# Creates a device+driver to manage the buttons.
# debug: flag for... debugging.
#
# Methods:
# setLinkedButtons(btA, btB, btC): links the physical buttons and the logical objects. If button A is
#     pressed/released then btA recieves the corrsponding event throug pressing/releasing in its center.
#     if the logical object is None, then point (0,0) will be acted upon.
# setLinkeButton(btnId, bt): links physical button id bntId (0 for button A etc.) and object bt. Same
#     idea as above.
#
class M5Buttons(BaseDevice):
    buttonID = {BUTTON_A_PIN: 0, BUTTON_B_PIN: 1, BUTTON_C_PIN: 2}
    
    def __init__(self, debug = False):
        self._linkedButtons = [None, None, None]
        self._phyButtons = [PCNTButton(BUTTON_A_PIN), PCNTButton(BUTTON_B_PIN), PCNTButton(BUTTON_C_PIN)]
        self._pressed = False
        self._changed = False
        self._bt = 0 # Button zero is special : it is at first supposed to be the released one...
        self._debug = debug
        self._points = [pt0, pt0, pt0] # lvgl will simulate a press at (0,0) if no logical object is linked
        self._driver = None
        self._devType = lv.INDEV_TYPE.BUTTON
    
    # Name? setLinkedObjects?
    def setLinkedButtons(self, btA, btB, btC):
        self._linkedButtons[0] = btA
        self._linkedButtons[1] = btB
        self._linkedButtons[2] = btC
        self.updatePoints()
    
    def setLinkedButton(self, btnId, bt):
        self._linkedButtons[btnId] = bt
        self.updatePoints()
    
    def update(self):
        p = False
        bt = self._bt
        for i in range(3):
            phy = self._phyButtons[i]
            if phy.pressed:
                p = True
                bt = i
                break
        if self._pressed != p or self._bt != bt:
            self._changed = True
        self._pressed = p
        self._bt = bt
    
    # Override
    def _reader(self, drv, data):
        self.update()
        data.btn_id = self._bt
        if self.pressed:
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        if self._debug and self.changed:
            print("Button reader: [{}] id: {}, state: {}".format(self, data.btn_id, data.state))
        return False

    def updatePoints(self):
        if self._driver is None:
            return
        for i in range(3):
            link = self._linkedButtons[i]
            if  link is None:
                self._points[i] = pt0
            else:
                self._points[i] = getCenter(link)        
        lv.indev_set_button_points(self._driver, self._points)
    
    # override
    def extraRegistration(self):
        self.updatePoints()

# To be removed...    
#     def registerDriverOLD(self):
#         self._indev_drv = lv.indev_drv_t()
#         lv.indev_drv_init(self._indev_drv)
#         self._indev_drv.type = lv.INDEV_TYPE.BUTTON
#         self._indev_drv.read_cb = self.getReader()
#         self._driver = lv.indev_drv_register(self._indev_drv)
#         self.updatePoints()
#         return self._driver

