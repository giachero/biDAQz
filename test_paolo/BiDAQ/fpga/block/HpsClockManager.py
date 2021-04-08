#!/usr/bin/python

from ..register import FpgaReg


class HpsClockManager:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()
        self.OscillatorFrequency = 50e6

    def SetUserClockDivider(self, Divider):
        self.FpgaReg.WriteBits("hps_pll_user1_clock", "DIVIDER", Divider - 1)

    def GetUserClockDivider(self):
        return self.FpgaReg.ReadBits("hps_pll_user1_clock", "DIVIDER") + 1

    def GetVcoNumerator(self):
        return self.FpgaReg.ReadBits("hps_pll_peripheral_vco", "NUMERATOR") + 1

    def GetVcoDenominator(self):
        return self.FpgaReg.ReadBits("hps_pll_peripheral_vco", "DENOMINATOR") + 1

    def GetUserClockFrequency(self):
        return self.OscillatorFrequency * self.GetVcoNumerator() / self.GetVcoDenominator() / self.GetUserClockDivider()

    def SetUserClockFrequency(self, Frequency):
        if Frequency > 16e6:
            Frequency = 16e6
        Divider = int(self.OscillatorFrequency * self.GetVcoNumerator() / self.GetVcoDenominator() / Frequency)
        if Divider > 500:
            Divider = 500
        self.SetUserClockDivider(Divider)
        return self.GetUserClockFrequency()
