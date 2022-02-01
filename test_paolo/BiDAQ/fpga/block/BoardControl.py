#!/usr/bin/python

from ..register import FpgaReg


class BoardControl:

    # Class constructor
    def __init__(self, BoardList=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(8))

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg(BoardList)

    def SetADCMode(self, Mode, Board=None):
        self.FpgaReg.SetBoardSettingNoGpio("BiDAQ_control_", "SER_PAR", Mode, Board)

    def SetADCModeSerial(self, Board=None):
        self.SetADCMode(0, Board)

    def SetADCModeParallel(self, Board=None):
        self.SetADCMode(1, Board)

    def GetADCMode(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_control_", "SER_PAR", Board)

    def SetSPIClockDivider(self, Divider, Board=None):
        self.FpgaReg.SetBoardSettingNoGpio("BiDAQ_control_", "SPI_CLK_DIV", Divider, Board)

    def GetSPIClockDivider(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_control_", "SPI_CLK_DIV", Board)

    def SetEnable(self, Enable, Board=None):
        self.FpgaReg.SetBoardSettingNoGpio("BiDAQ_control_", "EN", Enable, Board)

    def GetEnable(self, Board):
        return self.FpgaReg.GetBoardSetting("BiDAQ_control_", "EN", Board)

    def GetInData(self, Board, Channel):
        return self.FpgaReg.GetBoardSetting("BiDAQ_control_", "IN_DATA_{}".format(Channel), Board)

    def GetMonitorRegisters(self, BoardList=None, ChannelList=None):

        if BoardList is None:
            BoardList = self.FpgaReg.BoardList.copy()

        if ChannelList is None:
            ChannelList = list(range(0, 12))

        RetDict = dict()

        for Brd in BoardList:
            RetDict["Board_{}".format(Brd)] = dict()
            RetDict["Board_{}".format(Brd)]["Board"] = Brd
            RetDict["Board_{}".format(Brd)]["BoardControl"] = dict()
            for Ch in ChannelList:
                RetDict["Board_{}".format(Brd)]["BoardControl"]["Channel_{}".format(Ch)] = dict()
                RetDict["Board_{}".format(Brd)]["BoardControl"]["Channel_{}".format(Ch)]["Channel"] = Ch
                RetDict["Board_{}".format(Brd)]["BoardControl"]["Channel_{}".format(Ch)]["InData"] = \
                    self.GetInData(Brd, Ch)

        return RetDict
