#!/usr/bin/python

from ..register import FpgaReg


class DataPacketizer:

    # Class constructor
    def __init__(self, BoardList=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(0, 8))

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg(BoardList)

    def SetEnable(self, Enable, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "EN", Enable, Board)

    def GetEnable(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "EN", Board)

    def SetDropTimestamp(self, DropTimestamp, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "DROP_TIMESTAMP", DropTimestamp, Board)

    def GetDropTimestamp(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "DROP_TIMESTAMP", Board)

    def SetDropOnError(self, DropOnError, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "DROP_ON_ERROR", DropOnError, Board)

    def GetDropOnError(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "DROP_ON_ERROR", Board)

    def SetRTPPayloadType(self, PayloadType, Marker=True, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "RTP_PAYLOAD_TYPE", PayloadType | (Marker << 7), Board)

    def GetRTPPayloadType(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "RTP_PAYLOAD_TYPE", Board)

    def SetPacketSamples(self, Samples, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "PACKET_SAMPLES", Samples-1, Board)

    def GetPacketSamples(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PACKET_SAMPLES", Board)+1

    def SetRTPSource(self, Source, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "RTP_SOURCE", Source, Board)

    def GetRTPSource(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "RTP_SOURCE", Board)

    def SetPayloadHeader(self, Header, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "PAYLOAD_HEADER", Header, Board)

    def GetPayloadHeader(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PAYLOAD_HEADER", Board)

    def GetFIFOFillCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "FIFO_FILL_LEVEL", Board)

    def GetPacketCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PKT_CNT", Board)

    def GetDataCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "DAT_CNT", Board)

    def GetFIFOMaxFillCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "MAX_FILL_LEVEL", Board)

    def GetDroppedDataCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "CNT_DROPPED", Board)
