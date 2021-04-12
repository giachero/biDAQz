#!/usr/bin/python

from ..register import FpgaReg


class GpioControl:

    # Class constructor
    def __init__(self):

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "ENABLE", Enable)

    def GetEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "ENABLE")

    def SetCaptureEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "CAPTURE_ENABLE", Enable)

    def GetCaptureEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "CAPTURE_ENABLE")

    def SetId(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "ID", Enable)

    def GetId(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "ID")

    def GetPortEnable(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_ENABLE")

    def SetPortEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_ENABLE", 0xFF * Enable)

    def GetPinEnable(self, Pin):
        return (self.GetPortEnable() >> Pin) & 1

    def SetPinEnable(self, Pin, Enable):
        Curr = self.GetPortEnable()
        if Enable:
            New = Curr | (1 << Pin)
        else:
            New = Curr & ~(1 << Pin)
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_ENABLE", New)

    def GetPortDirection(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_DIRECTION")

    def SetPortDirection(self, Dir):
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_DIRECTION", 0xFF * Dir)

    def SetPortOutput(self):
        self.SetPortDirection(1)

    def SetPortInput(self):
        self.SetPortDirection(0)

    def GetPinDirection(self, Pin):
        return (self.GetPortDirection() >> Pin) & 1

    def SetPinDirection(self, Pin, Dir):
        Curr = self.GetPortDirection()
        if Dir:
            New = Curr | (1 << Pin)
        else:
            New = Curr & ~(1 << Pin)
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_DIRECTION", New)

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
        self.FpgaReg.FpgaMem.WriteBits("BiDAQ_gpio_control", "PIN_OUTPUT_VALUE", New)

    def GetPortInputValue(self):
        return self.FpgaReg.FpgaMem.ReadBits("BiDAQ_gpio_control", "PIN_INPUT_VALUE")

    def GetPinInputValue(self, Pin):
        return (self.GetPortInputValue() >> Pin) & 1
