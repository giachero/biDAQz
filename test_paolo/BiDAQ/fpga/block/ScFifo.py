#!/usr/bin/python

from ..register import FpgaReg


class ScFifo:

    # Class constructor
    def __init__(self, RegName):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()
        self.RegName = RegName

    def SetStoreAndForwardMode(self):
        self.SetCutThroughThr(0)

    def GetStoreAndForwardMode(self):
        return self.GetCutThroughThr() == 0

    def SetCutThroughMode(self, Thr=1):
        self.SetCutThroughThr(Thr)

    def GetCutThroughMode(self):
        return self.GetCutThroughThr() > 0

    def SetCutThroughThr(self, Thr):
        self.FpgaReg.WriteBits(self.RegName, "cut_through_threshold", Thr)

    def GetCutThroughThr(self):
        return self.FpgaReg.ReadBits(self.RegName, "cut_through_threshold")

    def GetFillLevel(self):
        return self.FpgaReg.ReadBits(self.RegName, "fill_level")

    def SetAlmostFullThr(self, Thr):
        self.FpgaReg.WriteBits(self.RegName, "almost_full_threshold", Thr)

    def GetAlmostFullThr(self):
        return self.FpgaReg.ReadBits(self.RegName, "almost_full_threshold")

    def SetAlmostEmptyThr(self, Thr):
        self.FpgaReg.WriteBits(self.RegName, "almost_empty_threshold", Thr)

    def GetAlmostEmptyThr(self):
        return self.FpgaReg.ReadBits(self.RegName, "almost_empty_threshold")

    def SetDropOnError(self, Value):
        self.FpgaReg.WriteBits(self.RegName, "drop_on_error", Value)

    def GetDropOnError(self):
        return self.FpgaReg.ReadBits(self.RegName, "drop_on_error")
