#!/usr/bin/python

from ..register import FpgaReg


class GpioControl:

    # Class constructor
    def __init__(self, BoardList=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(8))

        # Initialize register management class
        self.BoardList = BoardList.copy()
        self.FpgaReg = FpgaReg.FpgaReg(self.BoardList)

        self.FpgaReg.BoardList.pop(0)

    def SetEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "ENABLE", Enable)

    def GetEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "ENABLE")

    def SetCaptureEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "CAPTURE_ENABLE", Enable)

    def GetCaptureEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "CAPTURE_ENABLE")

    def SetId(self, ID):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "ID", ID)

    def GetId(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "ID")

    def GetPortEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_ENABLE")

    def SetPortEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_ENABLE", Enable)

    def GetPinEnable(self, Pin):
        return (self.GetPortEnable() >> Pin) & 1

    def SetPinEnable(self, Pin, Enable):
        Curr = self.GetPortEnable()
        if Enable:
            New = Curr | (1 << Pin)
        else:
            New = Curr & ~(1 << Pin)
        self.SetPortEnable(New)

    def GetPortDirection(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_DIRECTION")

    def SetPortDirection(self, Dir):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_DIRECTION", Dir)

    def SetPortOutput(self):
        self.SetPortDirection(0xFF)

    def SetPortInput(self):
        self.SetPortDirection(0x00)

    def GetPinDirection(self, Pin):
        return (self.GetPortDirection() >> Pin) & 1

    def SetPinDirection(self, Pin, Dir):
        Curr = self.GetPortDirection()
        if Dir:
            New = Curr | (1 << Pin)
        else:
            New = Curr & ~(1 << Pin)
        self.SetPortDirection(New)

    def SetPinOutput(self, Pin):
        self.SetPinDirection(Pin, 1)

    def SetPinInput(self, Pin):
        self.SetPinDirection(Pin, 0)

    def GetPortOutputValue(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_OUTPUT_VALUE")

    def SetPortOutputValue(self, Value):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_OUTPUT_VALUE", Value)

    def GetPinOutputValue(self, Pin):
        return (self.GetPortOutputValue() >> Pin) & 1

    def SetPinOutputValue(self, Pin, Value):
        Curr = self.GetPortOutputValue()
        if Value:
            New = Curr | (1 << Pin)
        else:
            New = Curr & ~(1 << Pin)
        self.SetPortOutputValue(New)

    def GetPortInputValue(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_INPUT_VALUE")

    def GetPinInputValue(self, Pin):
        return (self.GetPortInputValue() >> Pin) & 1

    def SetVirtualGpioEnable(self, Enable, Channel=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_virtual_gpio_control_", "ENABLE", Enable, Channel)

    def GetVirtualGpioEnable(self, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_virtual_gpio_control_", "ENABLE", Channel)

    def SetVirtualGpioValue(self, Value, Channel=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_virtual_gpio_control_", "VALUE", Value, Channel)

    def GetVirtualGpioValue(self, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_virtual_gpio_control_", "VALUE", Channel)
