#!/usr/bin/python

from ..register import FpgaReg


class DataPacketizer:

    # Class constructor
    def __init__(self, BoardList=None, Gpio=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(0, 8))

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg(BoardList, Gpio)

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
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "PACKET_SAMPLES", Samples - 1, Board)

    def GetPacketSamples(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PACKET_SAMPLES", Board) + 1

    def SetRTPSource(self, Source, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "RTP_SOURCE", Source, Board)

    def GetRTPSource(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "RTP_SOURCE", Board)

    def SetPayloadHeader(self, Header, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "PAYLOAD_HEADER", Header, Board)

    def GetPayloadHeader(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PAYLOAD_HEADER", Board)

    def GetFIFOFillCount(self, Board, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "FIFO_FILL_LEVEL_{}".format(Channel), Board)

    def GetPacketCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "PKT_CNT", Board)

    def GetDataCount(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "DAT_CNT", Board)

    def GetFIFOMaxFillCount(self, Board, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "MAX_FILL_LEVEL_{}".format(Channel), Board)

    def GetDroppedDataCount(self, Board, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_packetizer_", "CNT_DROPPED_{}".format(Channel), Board)

    def ResetCounters(self, Board=None, Channel=None):

        # Build channel list
        if Channel is None:
            ChannelList = list(range(0, 12))
        else:
            ChannelList = list(range(Channel, 1))

        # Reset channel registers
        for i in ChannelList:
            self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "FIFO_FILL_LEVEL_{}".format(i), 0, Board)
            self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "MAX_FILL_LEVEL_{}".format(i), 0, Board)
            self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "CNT_DROPPED_{}".format(i), 0, Board)

        # Reset block registers
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "PKT_CNT", 0, Board)
        self.FpgaReg.SetBoardSetting("BiDAQ_packetizer_", "DAT_CNT", 0, Board)

    def GetMonitorRegisters(self, BoardList=None, ChannelList=None):

        if BoardList is None:
            BoardList = self.FpgaReg.BoardList
            if self.FpgaReg.Gpio is not None:
                BoardList.append(self.FpgaReg.Gpio)

        if ChannelList is None:
            ChannelList = list(range(0, 12))

        RetDict = dict()

        for Brd in BoardList:
            RetDict["Board_{}".format(Brd)] = dict()
            RetDict["Board_{}".format(Brd)]["Board"] = Brd
            RetDict["Board_{}".format(Brd)]["DataPacketizer"] = dict()
            RetDict["Board_{}".format(Brd)]["DataPacketizer"]["SamplesSent"] = self.GetDataCount(Brd)
            RetDict["Board_{}".format(Brd)]["DataPacketizer"]["PacketsSent"] = self.GetPacketCount(Brd)
            if Brd == self.FpgaReg.Gpio:
                ChannelListCurr = list(range(0, self.FpgaReg.Gpio))
            else:
                ChannelListCurr = ChannelList
            for Ch in ChannelListCurr:
                RetDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)] = dict()
                RetDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)]["Channel"] = Ch
                RetDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)]["DroppedSamples"] = \
                    self.GetDroppedDataCount(Brd, Ch)
                RetDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)]["FIFOFillLevel"] = \
                    self.GetFIFOFillCount(Brd, Ch)
                RetDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)]["FIFOMaxFillLevel"] = \
                    self.GetFIFOMaxFillCount(Brd, Ch)

        return RetDict
