#!/usr/bin/python

from . import HpsRegDict
from . import Reg


############################################################
# Class to interface the System-on-Chip ARM and the HPS registers   #
############################################################
class HpsReg:

    # Class constructor
    def __init__(self):

        # Initialize FpgaRegDict class
        RegDictClass = HpsRegDict.HpsRegDict()

        # FPGA memory specs (BaseAdr is defined by Altera, MemLen by the last address used in the application)
        BaseAdr = 0xFF000000
        MemLen = 0x00400000
        # Initialize DevMem class
        self.HpsMem = Reg.Reg(BaseAdr, MemLen, RegDictClass.CreateDict())
