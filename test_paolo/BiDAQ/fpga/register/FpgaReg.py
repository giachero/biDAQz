#!/usr/bin/python

from . import FpgaRegDict
from . import Reg


############################################################
# Class to interface the System-on-Chip ARM and the FPGA   #
############################################################
class FpgaReg:

    # Class constructor
    def __init__(self, BoardList=None, Gpio=None):

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
        self.FpgaMem = Reg.Reg(BaseAdr, MemLen, RegDictClass.CreateDict(BoardList, Gpio))

    def SetBoardSettingGeneric(self, RegName, BitName, Data, Board=None, Gpio=None):
        Ret = 0
        if Board is None:
            IterList = self.BoardList.copy()
            if Gpio is not None:
                IterList.append(Gpio)
            for i in IterList:
                RegNameTmp = RegName + str(i)
                Ret = self.FpgaMem.WriteBits(RegNameTmp, BitName, Data)
                if Ret < 0:
                    raise Exception(
                        "SetBoardSetting error - RegName: {}, BitName: {}, Data: {}, Board: {}, Gpio: {}".format(
                            RegNameTmp, BitName, hex(Data), i, Gpio))
        else:
            Ret = self.FpgaMem.WriteBits(RegName + str(Board), BitName, Data)

        if Ret < 0:
            raise Exception("SetBoardSetting error - RegName: {}, BitName: {}, Data: {}, Board: {}, Gpio: {}".format(
                RegName, BitName, hex(Data), Board, Gpio))

    def SetBoardSetting(self, RegName, BitName, Data, Board=None):
        self.SetBoardSettingGeneric(RegName, BitName, Data, Board, self.Gpio)

    def SetBoardSettingNoGpio(self, RegName, BitName, Data, Board=None):
        self.SetBoardSettingGeneric(RegName, BitName, Data, Board)

    def GetBoardSetting(self, RegName, BitName, Board):
        return self.FpgaMem.ReadBits(RegName + str(Board), BitName)
