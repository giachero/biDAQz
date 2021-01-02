#!/usr/bin/python

from ..register import FpgaReg


class GeneralEnable:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetEnable(self, Enable):
        self.FpgaReg.WriteBits("pio_en_n", "EN_N", not Enable)

    def GetEnable(self):
        return not self.FpgaReg.ReadBits("pio_en_n", "EN_N")
