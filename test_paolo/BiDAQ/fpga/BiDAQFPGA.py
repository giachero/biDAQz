#!/usr/bin/python

from .block import BoardControl
from .block import DataPacketizer
from .block import GeneralEnable
from .block import HpsToTxMac
from .block import ScFifo
from .block import SyncGenerator
from .block import ClockRefGenerator
from .block import TxMac
from .block import UdpStreamer
from .block import SysId
from .register import FpgaReg
from functools import reduce


class BiDAQFPGA:

    # Class constructor
    def __init__(self, BoardList=None):

        # Init SysID block containing the number of boards
        self.SysId = SysId.SysId()
        # If no list is given, use the default number of boards stored in the SysID block
        if BoardList is None:
            BoardList = list(range(0, self.SysId.GetBoardNumber()))

        # Store board list
        self.BoardList = BoardList

        # Init the classes for each FPGA block
        self.BoardControl = BoardControl.BoardControl(BoardList)
        self.DataPacketizer = DataPacketizer.DataPacketizer(BoardList)
        self.SyncGenerator = SyncGenerator.SyncGenerator(BoardList)
        self.ClockRefGenerator = ClockRefGenerator.ClockRefGenerator()
        self.UdpStreamer = UdpStreamer.UdpStreamer()
        self.GeneralEnable = GeneralEnable.GeneralEnable()
        self.TxMac = TxMac.TxMac()
        self.HpsToTxMac = HpsToTxMac.HpsToTxMac()
        self.FifoHpsMac = ScFifo.ScFifo("sc_fifo_hps_mac")
        self.FifoOutDataAdapter = ScFifo.ScFifo("fifo_adapter_data")
        self.FifoOutData = ScFifo.ScFifo("sc_fifo_data")
        self.FifoTxMac = ScFifo.ScFifo("sc_fifo_tx_eth_tse")

        # Low level register access
        self.LL = FpgaReg.FpgaReg(BoardList)

    def __merge(self, a, b, path=None):

        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.__merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    def InitRtpSourceIds(self, Prefix, Crate, Half):

        for Brd in self.BoardList:
            Source = ((Prefix << 12) & 0xFFFFF000) | ((Crate << 8) & 0xF00) | (((Brd + 8*Half) << 4) & 0xF0)
            self.DataPacketizer.SetRTPSource(Source, Brd)

    def SetClockGeneratorMasterOrSlave(self, Master):

        if Master:
            MasterSetting = 1
            ClkSource = 0    # Clock source internal
            ClkOutEna = 1
            ClkInEna = 0
        else:
            MasterSetting = 0
            ClkSource = 1
            ClkOutEna = 0
            ClkInEna = 1

        self.GeneralEnable.SetMaster(MasterSetting)
        self.ClockRefGenerator.SetExternalInputEnable(ClkInEna)
        self.ClockRefGenerator.SetExternalOutputEnable(ClkOutEna)
        self.ClockRefGenerator.SetSource(ClkSource)

    def SetSlave(self):
        self.SetClockGeneratorMasterOrSlave(False)

    def SetMaster(self):
        self.SetClockGeneratorMasterOrSlave(True)


    def GetMonitorRegisters(self):

        DP = self.DataPacketizer.GetMonitorRegisters()
        SG = self.SyncGenerator.GetMonitorRegisters()
        US = self.UdpStreamer.GetMonitorRegisters()
        TM = self.TxMac.GetMonitorRegisters()
        HTM = self.HpsToTxMac.GetMonitorRegisters()
        Fifo = dict()
        FifoList = ("FifoHpsMac", "FifoOutDataAdapter", "FifoOutData", "FifoTxMac")
        for CurFifo in FifoList:
            Fifo[CurFifo] = dict()
            CurFifoAttr = getattr(self, CurFifo)
            Fifo[CurFifo]["FillLevel"] = CurFifoAttr.GetFillLevel()

        # MonitorDict = {**DP, **SG, **US, **TM, **HTM, **Fifo}
        MonitorDict = reduce(self.__merge, [DP, SG, US, TM, HTM, Fifo])

        return MonitorDict
