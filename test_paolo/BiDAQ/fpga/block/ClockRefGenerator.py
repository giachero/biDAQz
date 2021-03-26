#!/usr/bin/python

from ..register import FpgaReg


class ClockRefGenerator:

    # Class constructor
    def __init__(self):

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetEnable(self, Enable):
        self.FpgaReg.WriteBits("BiDAQ_sync_ref_generator", "ENABLE", Enable)

    def GetEnable(self):
        return self.FpgaReg.ReadBits("BiDAQ_sync_ref_generator", "ENABLE")

    def SetExternalOutputEnable(self, Enable):
        self.FpgaReg.WriteBits("BiDAQ_sync_ref_generator", "EXT_CLK_REF_OUT_ENA", Enable)

    def GetExternalOutputEnable(self):
        return self.FpgaReg.ReadBits("BiDAQ_sync_ref_generator", "EXT_CLK_REF_OUT_ENA")

    def SetExternalInputEnable(self, Enable):
        self.FpgaReg.WriteBits("BiDAQ_sync_ref_generator", "EXT_CLK_REF_IN_ENA", Enable)

    def GetExternalInputEnable(self):
        return self.FpgaReg.ReadBits("BiDAQ_sync_ref_generator", "EXT_CLK_REF_IN_ENA")

    def SetSource(self, Source):
        self.FpgaReg.WriteBits("BiDAQ_sync_ref_generator", "INT_CLK_REF_IN_SEL", Source)

    def GetSource(self):
        return self.FpgaReg.ReadBits("BiDAQ_sync_ref_generator", "INT_CLK_REF_IN_SEL")

    def SetSourceInternal(self):
        self.SetSource(0)

    def SetSourceExternal(self):
        self.SetSource(1)

    def SetDivider(self, Divider):
        Enable = self.GetEnable()
        if not Enable:
            self.FpgaReg.WriteBits("BiDAQ_sync_ref_generator", "DIVIDER", Divider - 1)
        else:
            raise Exception("Divider can't be set while ClockRef is enabled")

    def GetDivider(self):
        return self.FpgaReg.ReadBits("BiDAQ_sync_ref_generator", "DIVIDER") + 1

