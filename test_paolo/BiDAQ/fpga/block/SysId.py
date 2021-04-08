#!/usr/bin/python

from ..register import FpgaReg
from datetime import datetime


class SysId:

    # Class constructor
    def __init__(self):
        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def GetSysId(self):
        return self.FpgaReg.FpgaMem.ReadBits("sys_id", "SYSTEM_ID")

    def GetSysIdTimestamp(self):
        return self.FpgaReg.FpgaMem.ReadBits("sys_id", "SYSTEM_ID_TIMESTAMP")

    def GetBoardNumber(self):
        return (self.GetSysId() >> 8) & 0xF

    def GetFwRevision(self):
        return self.GetSysId() & 0xFF

    def GetSysIdDatetime(self):
        return datetime.fromtimestamp(self.GetSysIdTimestamp())
