#!/usr/bin/python

import netifaces

from ..register import FpgaReg


class TxMac:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetTxEnable(self, Enable):
        self.FpgaReg.WriteBits("eth_mac", "TX_ENA", Enable)

    def GetTxEnable(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_ENA")

    def SetReset(self, Reset):
        self.FpgaReg.WriteBits("eth_mac", "SW_RESET", Reset)

    def GetReset(self):
        return self.FpgaReg.ReadBits("eth_mac", "SW_RESET")

    def SetMac(self, MAC):
        self.FpgaReg.WriteBits("eth_mac", "MAC_1", MAC & 0xFFFF)
        self.FpgaReg.WriteBits("eth_mac", "MAC_0", (MAC >> 16) & 0xFFFFFFFF)

    def GetMac(self):
        MAC_LSB = self.FpgaReg.ReadBits("eth_mac", "MAC_1")
        MAC_MSB = self.FpgaReg.ReadBits("eth_mac", "MAC_0")
        return MAC_LSB | (MAC_MSB << 16)

    def SetPauseQuanta(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "PAUSE_QUANTA", Value)

    def GetPauseQuanta(self):
        return self.FpgaReg.ReadBits("eth_mac", "PAUSE_QUANTA")

    def SetRxSectionEmpty(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "RX_SECTION_EMPTY", Value)

    def GetRxSectionEmpty(self):
        return self.FpgaReg.ReadBits("eth_mac", "RX_SECTION_EMPTY")

    def SetRxSectionFull(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "RX_SECTION_FULL", Value)

    def GetRxSectionFull(self):
        return self.FpgaReg.ReadBits("eth_mac", "RX_SECTION_FULL")

    def SetTxSectionEmpty(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_SECTION_EMPTY", Value)

    def GetTxSectionEmpty(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_SECTION_EMPTY")

    def SetTxSectionFull(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_SECTION_FULL", Value)

    def GetTxSectionFull(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_SECTION_FULL")

    def SetRxAlmostEmpty(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "RX_ALMOST_EMPTY", Value)

    def GetRxAlmostEmpty(self):
        return self.FpgaReg.ReadBits("eth_mac", "RX_ALMOST_EMPTY")

    def SetRxAlmostFull(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "RX_ALMOST_FULL", Value)

    def GetRxAlmostFull(self):
        return self.FpgaReg.ReadBits("eth_mac", "RX_ALMOST_FULL")

    def SetTxAlmostEmpty(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_ALMOST_EMPTY", Value)

    def GetTxAlmostEmpty(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_ALMOST_EMPTY")

    def SetTxAlmostFull(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_ALMOST_FULL", Value)

    def GetTxAlmostFull(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_ALMOST_FULL")

    def SetTxIpgLength(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_Ipg_LENGTH", Value)

    def GetTxIpgLength(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_Ipg_LENGTH")

    def SetTxShift16(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "TX_SHIFT16", Value)

    def GetTxShift16(self):
        return self.FpgaReg.ReadBits("eth_mac", "TX_SHIFT16")

    def SetRxShift16(self, Value):
        self.FpgaReg.WriteBits("eth_mac", "RX_SHIFT16", Value)

    def GetRxShift16(self):
        return self.FpgaReg.ReadBits("eth_mac", "RX_SHIFT16")

    def GetStatisticsCounter(self, Name):
        return self.FpgaReg.ReadBits("eth_mac", Name)

    def Reset(self):

        self.SetReset(1)
        if not self.GetReset():
            raise Exception("MAC reset can't be set")
        self.SetReset(0)

    def Configure(self, FifoSize=2048):

        SectionThr = 0x10
        AlmostThr = 0x8
        TxAlmostFullThr = 0x3

        Interface = 'eth0'
        MacStr = netifaces.ifaddresses(Interface)[netifaces.AF_LINK][0]['addr']
        Mac = int(MacStr.replace(':', ''), 16)
        self.SetMac(Mac)
        self.SetPauseQuanta(0x2000)
        self.SetRxSectionEmpty(FifoSize - SectionThr)
        self.SetRxSectionFull(SectionThr)
        self.SetTxSectionEmpty(FifoSize - SectionThr)
        self.SetTxSectionFull(SectionThr)
        self.SetRxAlmostEmpty(AlmostThr)
        self.SetRxAlmostFull(AlmostThr)
        self.SetTxAlmostEmpty(AlmostThr)
        self.SetTxAlmostFull(TxAlmostFullThr)
        self.SetTxIpgLength(0xc)
        self.SetTxShift16(1)
        self.SetRxShift16(1)

    def StartTx(self):

        self.SetTxEnable(1)
        if not self.GetTxEnable():
            raise Exception("MAC TX enable can't be set")

    def Initialize(self):

        # noinspection PyBroadException
        try:
            self.Reset()
            self.Configure()
            self.Reset()
            self.StartTx()
        except:
            return -1
        return 0

    def GetMonitorRegisters(self):
        RetDict = dict()

        RetDict["TxMac"] = dict()
        RetDict["TxMac"]["PacketsSent"] = self.GetStatisticsCounter("aFramesTransmittedOK")
        RetDict["TxMac"]["BytesSent"] = self.GetStatisticsCounter("aOctetsTransmittedOK")
        RetDict["TxMac"]["PauseFrameSent"] = self.GetStatisticsCounter("aTxPAUSEMACCtrlFrames")
        RetDict["TxMac"]["ErrorPackets"] = self.GetStatisticsCounter("ifOutErrors")
        RetDict["TxMac"]["UnicastPackets"] = self.GetStatisticsCounter("ifOutUcastPkts")
        RetDict["TxMac"]["MulticastPackets"] = self.GetStatisticsCounter("ifOutMulticastPkts")
        RetDict["TxMac"]["BroadcastPackets"] = self.GetStatisticsCounter("ifOutBroadcastPkts")

        return RetDict
