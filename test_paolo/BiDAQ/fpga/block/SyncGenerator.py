#!/usr/bin/python

from ..register import FpgaReg


class SyncGenerator:

    # Class constructor
    def __init__(self, BoardList=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(0, 8))

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg(BoardList)
        self.BoardList = BoardList

    def SetReset(self, Reset, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "RESET", Reset, Board)

    def GetReset(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "RESET", Board)

    def SetTimestampReset(self, Reset, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "RESET_TIMESTAMP", Reset, Board)

    def GetTimestampReset(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "RESET_TIMESTAMP", Board)

    def Reset(self, Board=None):
        self.SetReset(1, Board)
        self.SetTimestampReset(1, Board)
        if self.GetReset(Board) & self.GetTimestampReset(Board):
            Err = False
        else:
            Err = True
        self.SetReset(0, Board)
        self.SetTimestampReset(0, Board)
        return -Err

    def SetEnable(self, Enable, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "ENABLE", Enable, Board)

    def GetEnable(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "ENABLE", Board)

    def SetDivider(self, Divider, Board=None):
        if Board is None:
            Enable = 0
            for i in self.BoardList:
                Enable |= self.GetEnable(i)
        else:
            Enable = self.GetEnable(Board)
        if not Enable:
            self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "DIVIDER", Divider - 1, Board)
        else:
            raise Exception("Divider can't be set while SyncGenerator is running")

    def GetDivider(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "DIVIDER", Board) + 1

    def SetPulseWidth(self, PulseWidth, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "PULSE_WIDTH", PulseWidth, Board)

    def GetPulseWidth(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "PULSE_WIDTH", Board)

    def SetTimestampResetValue(self, TimestampResetValue, Board=None):
        self.FpgaReg.SetBoardSetting("BiDAQ_sync_generator_", "TIMESTAMP_RESET_VALUE", TimestampResetValue, Board)

    def GetTimestampResetValue(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "TIMESTAMP_RESET_VALUE", Board)

    def GetTimestamp(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_sync_generator_", "TIMESTAMP", Board)

    def GetMonitorRegisters(self, BoardList=None):

        if BoardList is None:
            BoardList = self.FpgaReg.BoardList

        RetDict = dict()

        for Brd in BoardList:
            RetDict["Board_{}".format(Brd)] = dict()
            RetDict["Board_{}".format(Brd)]["Board"] = Brd
            RetDict["Board_{}".format(Brd)]["SyncGenerator"] = dict()
            RetDict["Board_{}".format(Brd)]["SyncGenerator"]["Timestamp"] = self.GetTimestamp(Brd)

        return RetDict
