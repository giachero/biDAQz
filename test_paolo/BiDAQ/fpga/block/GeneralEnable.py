#!/usr/bin/python

from ..register import FpgaReg


class GeneralEnable:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetEnable(self, Enable):
        self.FpgaReg.FpgaMem.WriteBits("pio_en_n", "EN_N", not Enable)

    def GetEnable(self):
        return not self.FpgaReg.FpgaMem.ReadBits("pio_en_n", "EN_N")

    def SetMaster(self, Master):
        self.FpgaReg.FpgaMem.WriteBits("pio_ms_out", "MASTER_OUT", Master)

    def GetMaster(self):
        return self.FpgaReg.FpgaMem.ReadBits("pio_ms_out", "MASTER_OUT")

    def ReadMaster(self):
        return int(not self.FpgaReg.FpgaMem.ReadBits("pio_ms_in", "MASTER_IN"))

    def SetStart(self, Start):
        self.FpgaReg.FpgaMem.WriteBits("pio_ms_out", "START_OUT", Start)

    def GetStart(self):
        return self.FpgaReg.FpgaMem.ReadBits("pio_ms_out", "START_OUT")

    def ReadStart(self):
        return int(not self.FpgaReg.FpgaMem.ReadBits("pio_ms_in", "START_IN"))
