#!/usr/bin/python

from ..register import FpgaReg


class HpsToTxMac:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetSpeed1G(self):
        self.FpgaReg.FpgaMem.WriteBits("hps_emac_interface_splitter", "MAC_SPEED", 0x0)

    def SetSpeed100M(self):
        self.FpgaReg.FpgaMem.WriteBits("hps_emac_interface_splitter", "MAC_SPEED", 0x3)

    def SetSpeed10M(self):
        self.FpgaReg.FpgaMem.WriteBits("hps_emac_interface_splitter", "MAC_SPEED", 0x2)

    def GetPacketCounter(self):
        return self.FpgaReg.FpgaMem.ReadBits("gmii_to_avalon_st_converter", "PKT_CNT")

    def GetDataCounter(self):
        return self.FpgaReg.FpgaMem.ReadBits("gmii_to_avalon_st_converter", "DAT_CNT")

    def GetMonitorRegisters(self):
        RetDict = dict()

        RetDict["HpsToMac"] = dict()
        RetDict["HpsToMac"]["DataSent"] = self.GetDataCounter()
        RetDict["HpsToMac"]["PacketsSent"] = self.GetPacketCounter()

        return RetDict
