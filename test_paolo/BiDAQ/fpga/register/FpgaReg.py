#!/usr/bin/python

from . import FpgaRegDict
from . import Reg


############################################################
# Class to interface the System-on-Chip ARM and the FPGA   #
############################################################
class FpgaReg:

    # Class constructor
    def __init__(self, BoardList=None, Gpio=False):

        # Store number of boards - THIS IS NOT USED ANYMORE!
        # self.NBoards = len(BoardList)

        # Store board list
        if BoardList is None:
            BoardList = []
        self.BoardList = BoardList

        # Store GPIO
        self.Gpio = Gpio

        # Initialize FpgaRegDict class
        RegDictClass = FpgaRegDict.FpgaRegDict()

        # FPGA memory specs (BaseAdr is defined by Altera, MemLen by the last address used in the application)
        BaseAdr = 0xC0000000
        MemLen = 0x00040000
        # Initialize DevMem class
        self.FpgaMem = Reg.Reg(BaseAdr, MemLen, RegDictClass.CreateDict(BoardList))

    def SetBoardSettingGeneric(self, RegName, BitName, Data, Board=None, Gpio=False):
        Ret = 0
        if Board is None:
            IterList = self.BoardList
            if Gpio:
                IterList.append(max(IterList) + 1)
            for i in IterList:
                Ret = self.FpgaMem.WriteBits(RegName + str(i), BitName, Data)
                if Ret < 0:
                    break
        else:
            Ret = self.FpgaMem.WriteBits(RegName + str(Board), BitName, Data)

        if Ret < 0:
            raise Exception("SetBoardSetting error - RegName: {}, BitName: {}".format(RegName, BitName))

    def SetBoardSetting(self, RegName, BitName, Data, Board=None):
        self.SetBoardSettingGeneric(RegName, BitName, Data, Board, self.Gpio)

    def SetBoardSettingNoGpio(self, RegName, BitName, Data, Board=None):
        self.SetBoardSettingGeneric(RegName, BitName, Data, Board)

    def GetBoardSetting(self, RegName, BitName, Board):
        return self.FpgaMem.ReadBits(RegName + str(Board), BitName)
