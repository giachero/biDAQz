#!/usr/bin/python

from ..register import FpgaReg


class BoardControl:

    # Class constructor
    def __init__(self, BoardList=None):

        # Default value
        if BoardList is None:
            BoardList = list(range(0, 8))

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
