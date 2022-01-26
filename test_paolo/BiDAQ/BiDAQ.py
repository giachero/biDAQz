#!/usr/bin/python

from board import BiDAQBoard
from fpga import BiDAQFPGA
from backplane import BiDAQBackplane
from firmware_flash import FirmwareFlash

import warnings
import logging
import sys
import optparse
import time
import pprint

log = logging.getLogger("BiDAQ")


# noinspection DuplicatedCode
class BiDAQ:
    """
    BiDAQ is the main class to control the Bicocca's DAQ (BiDAQ).

    Use this class to control the FPGA registers (through /dev/mem), the BiDAQ boards (through CAN bus), and the other
    peripherals on the backplane (through I2C).

    The class can be also used from the command line. Refer to the command line help (with option --help) for more
    information.

    :ivar Crate: Crate number (ID).
    :vartype Crate: int
    :ivar Half: Backplane half (0 or 1).
    :vartype Half: int
    :ivar BoardList: List of connected (and working) BiDAQ boards.
    :vartype BoardList: list of integers
    :ivar FPGA: Class to control FPGA registers.
    :vartype FPGA: :class:`fpga.BiDAQFPGA` class
    :ivar Board: List of classes to control the BiDAQ boards.
    :vartype Board: list of :class:`board.BiDAQBoard` classes
    :ivar Backplane: Class to control backplane functions.
    :vartype Backplane: :class:`backplane.BiDAQBackplane` class
    """

    def __init__(self, Crate=None, Half=None, BoardList=None, Verbose=False, Debug=False, LogToOutput=False):
        """
        :param Crate: Crate number. If None, it is read automatically using the I2C port expander.
        :type Crate: int
        :param Half: Backplane half. If None, it is read automatically using the I2C port expander.
        :type Half: int
        :param BoardList: List of connected boards. If None, the class will try to determine it automatically,
            using FPGA SysID register (to read how many blocks are instantiated) and querying boards with NOP commands
            through CAN bus.
        :type BoardList: list or tuple of integers
        :param Verbose: Logging verbosity. If True, set logging verbosity to INFO, otherwise leave to WARNING
        :type Verbose: bool
        """

        # Set log destination
        if LogToOutput:
            self.SetLogToOutput()
        else:
            self.SetLogToTmp()

        # Set verbosity
        if Debug:
            self.SetLogLevelDebug()
        elif Verbose:
            self.SetLogLevelInfo()
        else:
            self.SetLogLevelWarning()

        # Init the FPGA registers, if BoardList is None, the class will determine automatically the number of boards by
        # looking at the SysID register defined at build time
        self.FPGA = BiDAQFPGA.BiDAQFPGA(BoardList)

        # Init the backplane class
        if self.FPGA.SysId.GetFwRevision() > 4:
            self.Backplane = BiDAQBackplane.BiDAQBackplane()

        # Get Crate number from Backplane class, or set from input arguments
        if Crate is None:
            try:
                self.Crate = self.Backplane.Crate
            except AttributeError:
                self.Crate = 0
        else:
            self.Crate = Crate

        # Set crate Half from Backplane class, or set from input arguments
        if Half is None:
            try:
                self.Half = self.Backplane.Half
            except AttributeError:
                self.Half = 0
        else:
            self.Half = Half

        # Scan the boards and check if they reply to a NOP command
        self.Board, self.BoardList = self.InitBoards()

        log.info("Init complete - Crate: {}, Half: {}, BoardList: {}".format(self.Crate, self.Half, self.BoardList))

        # Disable powerdown for all boards
        if self.SetPowerdownDisableAll() < 0:
            log.warning("Can't disable powerdown on boards")

        # Start ADCs read for all boards
        if self.StartAdc() < 0:
            log.info("Can't start ADCs continuous read. Boards might be already enabled")

        # Initialize RTP source fields
        self.FPGA.InitRtpSourceIds(0xBDAC, self.Crate, self.Half)

    def __enter__(self):
        if self.SetPowerdownDisableAll() < 0:
            log.warning("Can't disable powerdown on boards")
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_traceback=None):
        if self.SetPowerdownEnableAll() < 0:
            log.warning("Can't re-enable powerdown on boards")
        for Brd in self.Board:
            Brd.CANNotifier.stop()

        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_value}')
            print(f'exc_traceback: {exc_traceback}')

    def InitBoards(self, NoWarning=False):
        """
        Initialize :class:`board.BiDAQBoard` class by checking that the boards are replying correctly. The function
        uses *BoardList* instance variable as the list of boards to scan.

        :return: A list of :class:`board.BiDAQBoard` classes and the new *BoardList*.
        :rtype: list of :class:`board.BiDAQBoard`, list of integers
        """
        Board = list()
        BoardList = self.FPGA.BoardList.copy()

        log.info("Initializing BiDAQ boards")
        log.info("Starting BoardList: {}".format(BoardList))

        for CurrentBoard in self.FPGA.BoardList:
            Board.append(BiDAQBoard.BiDAQBoard(self.Crate & 0xF, CurrentBoard + 8 * self.Half))
            CmdReply = Board[-1].NOP(NoWarning=NoWarning)
            if CmdReply.Status:
                Board[-1].CANNotifier.stop()
                Board.pop()
                BoardList.remove(CurrentBoard)
            else:
                Board[-1].InitBoard()
                Board[-1].StopDAQ(0)
        self.BoardList = BoardList

        if len(BoardList) is 0:
            if not NoWarning:
                log.warning("No boards found during initialization")

        log.info("Final BoardList: {}".format(BoardList))

        return Board, BoardList

    def FindBoardIdx(self, Brd):
        """
        Get board index from board number (if some boards are not installed, the board number is different than index).

        :param Brd: Board number.
        :type Brd: int
        :return: Board index (to be used with *self.Board[]* class list).
        :rtype: int
        """

        for BrdIdx in range(len(self.Board)):
            if (self.Board[BrdIdx].Board & 0x7) == Brd:
                return BrdIdx

        return None

    def SetPowerdownAll(self, Enable):

        Ret = 0
        if hasattr(self, 'BoardList') and hasattr(self, 'Board'):
            for Brd in self.BoardList:
                BrdIdx = self.FindBoardIdx(Brd)
                CmdReply = self.Board[BrdIdx].WritePowerdown(int(Enable), 0)
                if CmdReply.Status:
                    warnings.warn("Warning. WritePowerdown - Brd: {}, Status: {}, Value: {}".format(Brd,
                                                                                                    CmdReply.Status,
                                                                                                    CmdReply.Value))
                    Ret = CmdReply.Status
        return Ret

    def SetPowerdownEnableAll(self):
        return self.SetPowerdownAll(1)

    def SetPowerdownDisableAll(self):
        return self.SetPowerdownAll(0)

    def SetChannelConfigList(self, ConfigList):
        """
        Configure channels using a list or tuple.

        :param ConfigList:
            |   Channel configuration passed as a list of lists. Each element of the list must have 5
                elements: [Board, Channel, Input, Enable, Frequency]. Board is a list of boards (counting from 0), e.g.
                [0,1]. Channel is a list of channels (0 means all channels of the board, 1-12), e.g. [1,2,3,4]. Input
                is the setting for input connections (0=conn, 1=gnd, 2=vrefp or 3=vrefn). Enable is the setting
                to enable the Bessel filter (same options as before). Frequency is an int value for the Bessel filter
                cut-off frequency (valid values are from 24 to 2500).
            |   Example:
            |   [[[0,1],[1,2,3,4,5,6],0,True,24],[[0,1],[7,8,9,10,11,12],1,False,100]]
        :type ConfigList: list or tuple
        :return: Return status (a negative value means error).
        :rtype: int
        """
        Status = 0
        for Line in ConfigList:
            for Brd in Line[0]:
                for Channel in Line[1]:
                    Input = Line[2]
                    Enable = Line[3]
                    Freq = Line[4]
                    log.info(
                        "SetChannelConfig - Brd: {}, Ch: {} - Input: {}, Enable: {}, Frequency: {}".format(Brd,
                                                                                                           Channel,
                                                                                                           Input,
                                                                                                           Enable,
                                                                                                           Freq))
                    BrdIdx = self.FindBoardIdx(Brd)
                    CmdReply = self.Board[BrdIdx].WriteFilterSettingsWithADCCalibration(Channel, Freq, Enable, Input)
                    Status = CmdReply.Status
                    if CmdReply.Status:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        CmdReply.Status,
                                                                                                        CmdReply.Value)
                        )

        return Status

    def SetChannelConfigDict(self, ConfigDict):
        """
        Configure channels using a dictionary.

        :param ConfigDict: Channel configuration is passed as a dictionary or list of dictionaries. Each key or element
            is a dictionary which must have specific keys: 'Board' - list of boards (counting from 0), e.g. [0,1],
            'Channel' - list of channels (1-12, 0 means all), 'Ground' - setting for grounding the inputs (valid options
            are 0, 1, False or True), 'Enable' - setting to enable the Bessel filter (same options as before), 'Freq' -
            int value for the Bessel filter cut-off frequency (valid values are from 24 to 2500).
        :type ConfigDict: dict
        :return: Return status (a negative value means error).
        :rtype: int
        """
        Status = 0
        for Key in ConfigDict:
            for Brd in ConfigDict[Key]['Board']:
                for Channel in ConfigDict[Key]['Channel']:
                    Ground = ConfigDict[Key]['Ground']
                    Enable = ConfigDict[Key]['Enable']
                    Freq = ConfigDict[Key]['Freq']
                    log.info(
                        "SetChannelConfig - Brd: {}, Ch: {} - Grounded: {}, Enable: {}, Frequency: {}".format(Brd,
                                                                                                              Channel,
                                                                                                              Ground,
                                                                                                              Enable,
                                                                                                              Freq))
                    BrdIdx = self.FindBoardIdx(Brd)
                    CmdReply = self.Board[BrdIdx].WriteFilterSettingsWithADCCalibration(Channel, Freq, Enable, Ground)
                    Status = CmdReply.Status
                    if CmdReply.Status:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        CmdReply.Status,
                                                                                                        CmdReply.Value)
                        )
        return Status

    def SetFrequency(self, Frequency):
        """
        Set the DAQ frequency. The actual value that is set depends on which divider is available. Check the return
        values. The ADC samples the data at a higher frequency wrt the sync signal, because it uses its internal
        clock which is not synchronous and some margin must be provided.

        :param Frequency: Requested DAQ sampling frequency.
        :type Frequency: int
        :return: A list with status (a negative value means error), synchronization signal frequency (at least twice the
            requested DAQ frequency), and the ADC sampling frequency.
        """

        # Calculate the divider from the main 500 kHz clock. Value is rounded, actual DAQ frequency could be different
        SyncFreqDiv = round(500000 / (2 * Frequency))
        # This is the actual sync frequency set
        SyncFreq = 500000 / SyncFreqDiv
        # Init
        AdcFreq = 0
        Status = 0

        # Set the ADC sampling frequency with some margin (4%) to compensate for clock mismatch
        for i in range(0, len(self.Board)):
            CmdReply = self.Board[i].WriteADCFrequency(0, SyncFreq * 1.04)
            AdcFreq = CmdReply.Value
            Status = CmdReply.Status
            log.debug(
                "Board[brd].WriteADCFrequency - brd: {}, Status: {}, AdcFreq: {}".format(i, Status, AdcFreq))
            if Status < 0:
                return Status, 0, 0

        for i in self.FPGA.SyncGenerator.BoardList:
            if self.FPGA.SyncGenerator.GetEnable(i):
                return -1, 0, 0

        # Set the same divider on all the boards
        self.FPGA.SyncGenerator.SetDivider(SyncFreqDiv)
        log.debug("FPGA.SetDivider - SyncFreq: {}, SyncFreqDiv: {}".format(SyncFreq / 2, SyncFreqDiv))

        #        if self.FPGA.Gpio is not None:
        #            self.FPGA.SyncGenerator.SetDivider(SyncFreqDiv * 2, self.FPGA.Gpio)

        return Status, SyncFreq, AdcFreq

    def EnableGpio(self, VirtualGpioNumber=0, ADCParallelReadout=True):
        """
        Enable GPIO capture. The optional argument allow to enable also up to 7 24-bit virtual GPIOs.

        :param VirtualGpioNumber: Number of virtual GPIOs to be enabled (0-7).
        :type VirtualGpioNumber: int
        :param ADCParallelReadout: Flag to set ADC parallel readout on all boards
        :type ADCParallelReadout: bool
        """

        self.FPGA.GpioControl.SetCaptureEnable(1)
        self.FPGA.GpioControl.SetEnable(1)
        for i in list(range(1, VirtualGpioNumber + 1)):
            self.FPGA.GpioControl.SetVirtualGpioEnable(1, i)

        # If parallel readout is enabled, then enable it on all boards, otherwise only few GPIOs pins corresponding to
        # the active boards will be used as GPIOs (parallel/serial setting takes precedence even if some board is not
        # enabled for DAQ)
        if ADCParallelReadout:
            self.FPGA.BoardControl.SetADCModeParallel()

    def ReadAdcGenericN(self, Board, N, GetInputValueFcn):
        ValList = [0] * 12
        TimestampList = [-1] * 12
        Timeout = self.FPGA.SyncGenerator.GetDivider(Board) / 500000 * 2 * 1.1 + 0.001
        for i in range(N):
            for Ch in range(12):
                Val = TimestampList[Ch]
                Start = time.time()
                while Val == TimestampList[Ch]:
                    if (time.time() - Start) > Timeout:
                        log.error("Error. Timeout while reading data")
                        return -1
                    Val = self.FPGA.SyncGenerator.GetTimestamp(Board)
                TimestampList[Ch] = Val
                Val = GetInputValueFcn(Board, Ch)
                ValList[Ch] = (ValList[Ch] * i + Val) / (i + 1)
        return ValList

    def ReadAdcValueN(self, Board, N):
        return self.ReadAdcGenericN(Board, N, self.GetInputValue)

    def ReadAdcVoltageN(self, Board, N):
        return self.ReadAdcGenericN(Board, N, self.GetInputVoltage)

    def SaveChannelSetting(self, Board):

        FilterInput = list(range(12))
        FilterFreq = list(range(12))
        FilterEnable = list(range(12))

        for Ch in range(12):

            CmdReply = self.Board[Board].ReadInputGrounded(Ch + 1)
            if CmdReply.Status:
                log.warning("Warning. ReadInputGrounded - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
            FilterInput[Ch] = CmdReply.Value

            CmdReply = self.Board[Board].ReadFilterFrequency(Ch + 1)
            if CmdReply.Status:
                log.warning("Warning. ReadFilterFrequency - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
            FilterFreq[Ch] = CmdReply.Value

            CmdReply = self.Board[Board].ReadFilterEnable(Ch + 1)
            if CmdReply.Status:
                log.warning("Warning. ReadFilterEnable - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
            FilterEnable[Ch] = CmdReply.Value

            return 0, FilterInput, FilterFreq, FilterEnable

    def RestoreChannelSetting(self, Board, FilterInput, FilterFreq, FilterEnable):

        for Ch in range(12):

            CmdReply = self.Board[Board].WriteInputGrounded(Ch, FilterInput[Ch])
            if CmdReply.Status:
                log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status

            CmdReply = self.Board[Board].WriteFilterFrequency(Ch, FilterFreq[Ch])
            if CmdReply.Status:
                log.warning("Warning. WriteFilterFrequency - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status

            CmdReply = self.Board[Board].WriteFilterEnableWithADCCalibration(Ch, FilterEnable[Ch])
            if CmdReply.Status:
                log.warning("Warning. WriteFilterEnableWithADCCalibration - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status

            return 0

    def CalibrateOffsetWithCurrentSettings(self, Board, DaqFreq, AvgN=100, Pause=0.2, OffsetThr=10):
        log.info("Calibration started - Offset - Current settings")
        log.info("Board:        {}".format(Board))
        log.info("AvgN:         {}".format(AvgN))
        log.info("Pause:        {}".format(Pause))
        log.info("DaqFreq:      {}".format(DaqFreq))

        self.StopDaq(True)
        self.StartAdc(DaqFreq)
        time.sleep(Pause)
        Data = self.ReadAdcValueN(Board, AvgN)
        self.StopDaq(True)
        GainCurr = list(range(12))
        for Ch in range(12):
            CmdReply = self.Board[Board].ReadADCCalibration(Ch + 1, 0)
            if CmdReply.Status:
                log.warning(
                    "Warning. ReadADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(Board, Ch + 1,
                                                                                                 CmdReply.Status,
                                                                                                 CmdReply.Value))
                return CmdReply.Status
            OffsetCurr = CmdReply.Value
            CmdReply = self.Board[Board].ReadADCCalibration(Ch + 1, 1)
            if CmdReply.Status:
                log.warning(
                    "Warning. ReadADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(Board, Ch + 1,
                                                                                                 CmdReply.Status,
                                                                                                 CmdReply.Value))
                return CmdReply.Status
            GainCurr[Ch] = CmdReply.Value
            OffsetNew = OffsetCurr + round((Data[Ch] - 0x800000) * 0x400000 / GainCurr[Ch])
            log.info("Offset calibration - Ch: {}, Data: 0x{:X}, OffsetCurr: 0x{:X}, OffsetNew: 0x{:X}".format(
                Ch, int(round(Data[Ch])), OffsetCurr, OffsetNew))
            CmdReply = self.Board[Board].WriteADCCalibration(Ch + 1, 0, OffsetNew)
            if CmdReply.Status:
                log.warning(
                    "Warning. WriteADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(Board, Ch + 1,
                                                                                                  CmdReply.Status,
                                                                                                  CmdReply.Value))
                return CmdReply.Status
        self.StartAdc(DaqFreq)
        time.sleep(Pause)
        DataAfter = self.ReadAdcValueN(Board, AvgN)
        for Ch in range(12):
            DeltaOff = round(DataAfter[Ch] - 0x800000)
            log.info("Offset result - Ch: {}, DataBefore: 0x{:X}, DataAfter: 0x{:X}, Error: {}".format(
                Ch, int(round(Data[Ch])), int(round(DataAfter[Ch])), DeltaOff))
            if abs(DeltaOff) > OffsetThr:
                log.warning(
                    "Warning. Offset calibration out of threshold - Brd: {}, Ch {}, Delta: {}".format(Board, Ch + 1,
                                                                                                      DeltaOff))
        self.StopDaq(True)
        self.StartAdc()

        return 0

    def CalibrateOffset(self, Board, FilterEnable=1, AvgN=100, OffsetThr=10, Pause=0.2, DaqFreq=100, FilterFreq=24):
        log.info("Calibration started - Offset")
        log.info("Board:        {}".format(Board))
        log.info("FilterEnable: {}".format(FilterEnable))
        log.info("AvgN:         {}".format(AvgN))
        log.info("OffsetThr:    {}".format(OffsetThr))
        log.info("Pause:        {}".format(Pause))
        log.info("DaqFreq:      {}".format(DaqFreq))
        log.info("FilterFreq:   {}".format(FilterFreq))

        Status, FilterInputOld, FilterFreqOld, FilterEnableOld = self.SaveChannelSetting(Board)
        if Status:
            log.warning("Warning. SaveChannelSetting - Brd: {}, Status: {}".format(Board, Status))
            return Status

        CmdReply = self.Board[Board].WriteFilterSettingsWithADCCalibration(0, FilterFreq, FilterEnable, 1)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status

        Status = self.CalibrateOffsetWithCurrentSettings(Board, DaqFreq, AvgN, Pause, OffsetThr)
        if Status:
            log.warning("Warning. CalibrateOffsetWithCurrentSettings - Brd: {}, Status: {}".format(Board, Status))
            return Status

        Status = self.RestoreChannelSetting(Board, FilterInputOld, FilterFreqOld, FilterEnableOld)
        if Status:
            log.warning("Warning. WriteChannelSetting - Brd: {}, Status: {}".format(Board, Status))
            return Status

        return 0

    def CalibrateGain(self, Board, SaveInMemory=False, FilterEnable=1, AvgN=100, GainThrPpm=3, Pause=0.2, DaqFreq=100,
                      FilterFreq=24):
        log.info("Calibration started - Gain")
        log.info("Board:        {}".format(Board))
        log.info("SaveInMemory: {}".format(SaveInMemory))
        log.info("FilterEnable: {}".format(FilterEnable))
        log.info("AvgN:         {}".format(AvgN))
        log.info("GainThrPpm:   {}".format(GainThrPpm))
        log.info("Pause:        {}".format(Pause))
        log.info("DaqFreq:      {}".format(DaqFreq))
        log.info("FilterFreq:   {}".format(FilterFreq))

        self.StopDaq(True)

        Status, FilterInputOld, FilterFreqOld, FilterEnableOld = self.SaveChannelSetting(Board)
        if Status:
            log.warning("Warning. SaveChannelSetting - Brd: {}, Status: {}".format(Board, Status))
            return Status

        CmdReply = self.Board[Board].WriteFilterSettingsWithADCCalibration(0, FilterFreq, FilterEnable, 2)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status
        GainCurr = list(range(12))
        for Ch in range(12):
            CmdReply = self.Board[Board].ReadADCCalibration(Ch + 1, 1)
            if CmdReply.Status:
                log.warning(
                    "Warning. ReadADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(
                        Board, Ch + 1, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
            GainCurr[Ch] = CmdReply.Value
        self.StartAdc(DaqFreq)
        time.sleep(Pause)
        DataPos = self.ReadAdcVoltageN(Board, AvgN)
        CmdReply = self.Board[Board].WriteInputGrounded(0, 3)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status
        time.sleep(Pause)
        DataNeg = self.ReadAdcVoltageN(Board, AvgN)
        self.StopDaq(True)
        GainError = list(range(12))
        GainNew = list(range(12))
        for Ch in range(12):
            GainError[Ch] = (DataPos[Ch] - DataNeg[Ch]) / 10
            GainNew[Ch] = round(GainCurr[Ch] / GainError[Ch])
            log.info(
                "Gain calibration - Ch: {}, DataP: {:.6f}, DataN: {:.6f}, Gain: 0x{:X}, GainErr: {:.2f} ppm, GainNew: "
                "0x{:X}".format(Ch, DataPos[Ch], DataNeg[Ch], GainCurr[Ch], (GainError[Ch] - 1) * 1e6, GainNew[Ch]))
            CmdReply = self.Board[Board].WriteADCCalibration(Ch + 1, 1, GainNew[Ch])
            if CmdReply.Status:
                log.warning(
                    "Warning. WriteADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(
                        Board, Ch + 1, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
        self.StartAdc(DaqFreq)
        time.sleep(Pause)
        DataNegNew = self.ReadAdcVoltageN(Board, AvgN)
        CmdReply = self.Board[Board].WriteInputGrounded(0, 2)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status
        time.sleep(Pause)
        DataPosNew = self.ReadAdcVoltageN(Board, AvgN)
        self.StopDaq(True)
        for Ch in range(12):
            GainErrorBeforePpm = (GainError[Ch] - 1) * 1e6
            GainErrorAfterPpm = ((DataPosNew[Ch] - DataNegNew[Ch]) / 10 - 1) * 1e6
            log.info(
                "Gain result - Ch: {}, GainErrorBefore: {:.2f} ppm, GainErrorAfterPpm: {:.2f} ppm".format(
                    Ch, GainErrorBeforePpm, GainErrorAfterPpm))
            if abs(GainErrorAfterPpm) > GainThrPpm:
                log.warning(
                    "Warning. Gain calibration out of threshold - Brd: {}, Ch {}, Error: {:.2f} ppm".format(
                        Board, Ch + 1, GainErrorAfterPpm))
            if SaveInMemory:
                if FilterEnable:
                    MemoryAdr = 1
                else:
                    MemoryAdr = 2
                CmdReply = self.Board[Board].SaveADCCalibration(Ch + 1, MemoryAdr)
                if CmdReply.Status:
                    log.warning(
                        "Warning. SaveADCCalibration - Brd: {}, Ch {}, Status: {}, Value: {}".format(
                            Board, Ch + 1, CmdReply.Status, CmdReply.Value))
                    return CmdReply.Status

        Status = self.RestoreChannelSetting(Board, FilterInputOld, FilterFreqOld, FilterEnableOld)
        if Status:
            log.warning("Warning. WriteChannelSetting - Brd: {}, Status: {}".format(Board, Status))
            return Status

        self.StartAdc()

        return 0

    def CheckGainCalibration(self, Board, DaqFreq, AvgN=100, GainThrPpm=3, Pause=0.2):

        log.info("Check gain error started - Board {}".format(Board))

        FilterInput = list(range(12))
        for Ch in range(12):
            CmdReply = self.Board[Board].ReadInputGrounded(Ch + 1)
            if CmdReply.Status:
                log.warning("Warning. ReadInputGrounded - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
            FilterInput[Ch] = CmdReply.Value

        self.StopDaq(True)
        # self.Board[Board].WriteADCInputBufferEnable(0, 0)
        self.StartAdc(DaqFreq)
        CmdReply = self.Board[Board].WriteInputGrounded(0, 3)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status
        time.sleep(Pause)
        DataNeg = self.ReadAdcVoltageN(Board, AvgN)
        CmdReply = self.Board[Board].WriteInputGrounded(0, 2)
        if CmdReply.Status:
            log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(Board, CmdReply.Status,
                                                                                              CmdReply.Value))
            return CmdReply.Status
        time.sleep(Pause)
        DataPos = self.ReadAdcVoltageN(Board, AvgN)
        self.StopDaq(True)
        Status = 0
        GainErrorPpm = [0.] * 12
        for Ch in range(12):
            GainErrorPpm[Ch] = ((DataPos[Ch] - DataNeg[Ch]) / 10 - 1) * 1e6
            log.info(
                "Gain calibration - Ch: {}, DataP: {:.6f}, DataN: {:.6f}, GainErr: {:.2f} ppm,".format(
                    Ch, DataPos[Ch], DataNeg[Ch], GainErrorPpm[Ch]))
            if abs(GainErrorPpm[Ch]) > GainThrPpm:
                log.warning(
                    "Warning. Gain error out of threshold - Brd: {}, Ch {}, Error: {:.2f} ppm".format(
                        Board, Ch + 1, GainErrorPpm[Ch]))
                Status = 1
            CmdReply = self.Board[Board].WriteInputGrounded(Ch, FilterInput[Ch])
            if CmdReply.Status:
                log.warning("Warning. WriteInputGrounded - Brd: {}, Status: {}, Value: {}".format(
                    Board, CmdReply.Status, CmdReply.Value))
                return CmdReply.Status
        self.StartAdc()
        return Status, GainErrorPpm

    def CheckGainCalibrationAllBoards(self, DaqFreq, AvgN=100, GainThrPpm=3, Pause=0.2):
        Status = 0
        GainErrorPpm = list()
        for Brd in self.BoardList:
            BrdIdx = self.FindBoardIdx(Brd)
            Status, GainErrorPpmTmp = self.CheckGainCalibration(BrdIdx, DaqFreq, AvgN, GainThrPpm, Pause)
            if Status < 0:
                log.warning("Warning. Failed board {} gain check".format(Brd))
            elif Status > 0:
                log.warning("Warning. Board {} gain out of threshold".format(Brd))
            GainErrorPpm = GainErrorPpm + [GainErrorPpmTmp]
        return Status, GainErrorPpm

    def CalibrateBoard(self, Board, SaveInMemory=False, AvgN=100, OffsetThr=10, GainThrPpm=3, Pause=0.2, DaqFreq=100,
                       FilterFreq=24):

        log.info("Calibration started")
        log.info("Board:        {}".format(Board))
        log.info("SaveInMemory: {}".format(SaveInMemory))
        log.info("AvgN:         {}".format(AvgN))
        log.info("OffsetThr:    {}".format(OffsetThr))
        log.info("GainThrPpm:   {}".format(GainThrPpm))
        log.info("Pause:        {}".format(Pause))
        log.info("DaqFreq:      {}".format(DaqFreq))
        log.info("FilterFreq:   {}".format(FilterFreq))

        if self.CalibrateOffset(Board, True, AvgN, OffsetThr, Pause, DaqFreq, FilterFreq):
            log.warning("Warning. Failed offset calibration")
            return -1
        if self.CalibrateGain(Board, SaveInMemory, True, AvgN, GainThrPpm, Pause, DaqFreq, FilterFreq):
            log.warning("Warning. Failed gain calibration")
            return -1
        if self.CalibrateOffset(Board, False, AvgN, OffsetThr, Pause, DaqFreq, FilterFreq):
            log.warning("Warning. Failed offset calibration")
            return -1
        if self.CalibrateGain(Board, SaveInMemory, False, AvgN, GainThrPpm, Pause, DaqFreq, FilterFreq):
            log.warning("Warning. Failed gain calibration")
            return -1
        return 0

    def CalibrateAllBoards(self, SaveInMemory=False, AvgN=100, OffsetThr=10, GainThrPpm=3, Pause=0.2, DaqFreq=100,
                           FilterFreq=24):
        Status = 0
        for Brd in self.BoardList:
            BrdIdx = self.FindBoardIdx(Brd)
            if self.CalibrateBoard(
                    BrdIdx, SaveInMemory, AvgN, OffsetThr, GainThrPpm, Pause, DaqFreq, FilterFreq):
                log.warning("Warning. Failed board {} calibration".format(Brd))
                Status = -1
        return Status

    # Start just ADC readout from FPGA, without sending out any data
    def StartAdc(self, Frequency=1000, AdcParallelReadout=True, BoardList=None):
        """
        Start the DAQ.

        :param Frequency: Desired DAQ frequency.
        :type Frequency: int
        :param AdcParallelReadout: Set ADC parallel readout.
        :type AdcParallelReadout: bool
        :param BoardList: Set list of boards to be started (None starts all).
        :type BoardList: list or tuple or None
        :return: Return status (a negative value means error).
        :rtype: int
        """

        if BoardList is None:
            BoardListCurr = self.BoardList
        else:
            BoardListCurr = BoardList

        for Brd in BoardListCurr:
            BrdIdx = self.FindBoardIdx(Brd)
            CmdReply = self.Board[BrdIdx].ReadDAQRunning(0)
            if CmdReply.Status:
                log.warning("Warning. ReadDAQRunning - Brd: {}, Status: {}, Value: {}".format(BrdIdx, CmdReply.Status,
                                                                                              CmdReply.Value))
                return CmdReply.Status
            if CmdReply.Value:
                log.info("At least one board is already in continuous DAQ mode")
                return -1

        Status, SyncFreq, AdcFreq = self.SetFrequency(Frequency)
        if Status < 0:
            log.warning("Couldn't set DAQ frequency")
            return Status
        if AdcFreq < SyncFreq * 1.04:
            log.warning("DAQ freq is too high (AdcFreq: {}, SyncFreq: {})".format(AdcFreq, SyncFreq))
            return -1

        for Brd in BoardListCurr:
            BrdIdx = self.FindBoardIdx(Brd)
            CmdReply = self.Board[BrdIdx].WriteADCMode(AdcParallelReadout + 1)
            if CmdReply.Status:
                log.warning("Warning. WriteADCMode - Brd: {}, Status: {}, Value: {}".format(BrdIdx, CmdReply.Status,
                                                                                            CmdReply.Value))
                return CmdReply.Status
            CmdReply = self.Board[BrdIdx].StartDAQ(0)
            if CmdReply.Status:
                log.warning("Warning. StartDAQ - Brd: {}, Status: {}, Value: {}".format(BrdIdx, CmdReply.Status,
                                                                                        CmdReply.Value))
                return CmdReply.Status

        for Brd in BoardListCurr:
            # Enable the SPI block
            self.FPGA.BoardControl.SetADCMode(AdcParallelReadout, Brd)
            self.FPGA.BoardControl.SetEnable(1, Brd)

        # General enable (this is obsolete)
        self.FPGA.GeneralEnable.SetEnable(1)

        # Setup the sync generator block
        for Brd in BoardListCurr:
            if self.FPGA.SysId.GetFwRevision() > 4:
                self.FPGA.SyncGenerator.SetTimestampResetValue(0xFFFFFFFF, Brd)
            self.FPGA.SyncGenerator.Reset(Brd)
            self.FPGA.SyncGenerator.SetEnable(1, Brd)

        # Each FPGA runs from its own clock, they are synced only when the DAQ is started (with StartDaq method)
        self.FPGA.SetSlave()

        # Start the acquisition by applying the sync clock, in common to all boards
        self.FPGA.ClockRefGenerator.SetEnable(1)

        return 0

    def ResetBoards(self, Timeout=30):

        self.StopDaq(True, True)

        OldBoards = self.BoardList
        self.BoardList = None

        self.Backplane.PortExpander.ResetBoards()

        StartTime = time.time()
        while (time.time() - StartTime) < Timeout:
            self.Board, self.BoardList = self.InitBoards(NoWarning=True)
            if self.BoardList == OldBoards:
                break
            else:
                time.sleep(0.5)

        if self.BoardList != OldBoards:
            log.error("Some boards did not reply after restart")
            return -1
        else:
            log.info("Init complete - Crate: {}, Half: {}, BoardList: {}".format(self.Crate, self.Half, self.BoardList))

        # Disable powerdown for all boards
        if self.SetPowerdownDisableAll() < 0:
            log.warning("Can't disable powerdown on boards")

        # Start ADCs read for all boards
        if self.StartAdc() < 0:
            log.info("Can't start ADCs continuous read. Boards might be already enabled")

        return 0

    # Start DAQ
    def StartDaq(self, IpAdrDst, UdpPortDst, Frequency, SamplesPerPacket=180, AdcParallelReadout=True,
                 DropTimestamp=True, RTPPayloadType=20, BoardList=None, Gpio=False):
        """
        Start the DAQ.

        :param IpAdrDst: Destination IP address.
        :type IpAdrDst: int
        :param UdpPortDst: Destination and source UDP ports.
        :type UdpPortDst: int
        :param Frequency: Desired DAQ frequency.
        :type Frequency: int
        :param SamplesPerPacket: Number of samples in each RTP packet.
        :type SamplesPerPacket: int
        :param AdcParallelReadout: Set ADC parallel readout.
        :type AdcParallelReadout: bool
        :param DropTimestamp: Drop timestamps from the output data stream.
        :type DropTimestamp: bool
        :param RTPPayloadType: Set RTP payload type header field.
        :type RTPPayloadType: int
        :param BoardList: Set list of boards to be started (None starts all).
        :type BoardList: list or tuple or None
        :param Gpio: Set GPIO enable
        :type Gpio: bool
        :return: Return status (a negative value means error).
        :rtype: int
        """

        Status = self.StopDaq(True)
        if Status < 0:
            log.warning("Couldn't stop DAQ")
            return Status

        Status, SyncFreq, AdcFreq = self.SetFrequency(Frequency)
        if Status < 0:
            log.warning("Couldn't set DAQ frequency")
            return Status
        if AdcFreq < SyncFreq * 1.04:
            log.warning("DAQ freq is too high (AdcFreq: {}, SyncFreq: {})".format(AdcFreq, SyncFreq))
            return -1

        if BoardList is None:
            BoardListCurr = self.BoardList  # list(range(len(self.Board)))
        else:
            BoardListCurr = BoardList

        for Brd in BoardListCurr:
            BrdIdx = self.FindBoardIdx(Brd)
            CmdReply = self.Board[BrdIdx].WriteADCMode(AdcParallelReadout + 1)
            if CmdReply.Status:
                log.warning("Warning. WriteADCMode - Brd: {}, Status: {}, Value: {}".format(BrdIdx, CmdReply.Status,
                                                                                            CmdReply.Value))
                return CmdReply.Status

            # CmdRep = self.Board[BrdIdx].WriteADCInputBufferEnable(0, 0)
            # if CmdRep.Status:
            #     log.warning("Warning. WriteADCInputBufferEnable - Brd: {}, Status: {}, Value: {}".format(BrdIdx,
            #                                                                                              CmdRep.Status,
            #                                                                                              CmdRep.Value))
            #     return CmdReply.Status

            CmdReply = self.Board[BrdIdx].StartDAQ(0)
            if CmdReply.Status:
                log.warning("Warning. StartDAQ - Brd: {}, Status: {}, Value: {}".format(BrdIdx, CmdReply.Status,
                                                                                        CmdReply.Value))
                return CmdReply.Status

        # Setup the UDP packet creator with own and destination addresses
        self.FPGA.UdpStreamer.SetUdpStreamEnable(0)
        self.FPGA.UdpStreamer.AutoSetUdpStreamSourAddr()
        self.FPGA.UdpStreamer.SetUdpStreamDestIp(IpAdrDst)
        self.FPGA.UdpStreamer.AutoSetUdpStreamDestMac()
        self.FPGA.UdpStreamer.SetUdpStreamDestPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamSourPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamEnable(1)

        for Brd in BoardListCurr:
            # Enable the SPI block
            self.FPGA.BoardControl.SetADCMode(AdcParallelReadout, Brd)
            self.FPGA.BoardControl.SetEnable(1, Brd)

        BoardListCurrGpio = BoardListCurr.copy()
        if Gpio:
            BoardListCurrGpio.append(self.FPGA.Gpio)

        for Brd in BoardListCurrGpio:

            # Setup the RTP packet creator
            self.FPGA.DataPacketizer.SetDropTimestamp(DropTimestamp, Brd)
            self.FPGA.DataPacketizer.SetPacketSamples(SamplesPerPacket, Brd)

            RTPPayloadTypeTmp = (RTPPayloadType & 0xFC)
            if not Gpio or Brd < self.FPGA.Gpio:
                BrdIdx = self.FindBoardIdx(Brd)
                CmdReply = self.Board[BrdIdx].ReadLatestHWRevision()
                LatestHWRevision = CmdReply.Value
                if CmdReply.Status:
                    log.warning("Warning. ReadLatestHWRevision - Brd: {}, Status: {}".format(BrdIdx, CmdReply.Status))
                    return CmdReply.Status
                CmdReply = self.Board[BrdIdx].ReadFilterEnable(1)
                FilterEnable = CmdReply.Value
                if CmdReply.Status:
                    log.warning("Warning. ReadFilterEnable - Brd: {}, Status: {}".format(BrdIdx, CmdReply.Status))
                    return CmdReply.Status
                RTPPayloadTypeTmp = RTPPayloadTypeTmp | (LatestHWRevision << 1) | FilterEnable

            self.FPGA.DataPacketizer.SetRTPPayloadType(RTPPayloadTypeTmp, True, Brd)
            self.FPGA.DataPacketizer.SetPayloadHeader(self.FPGA.SyncGenerator.GetDivider(Brd), Brd)
            self.FPGA.DataPacketizer.SetEnable(1, Brd)

        # Powerdown all boards
        if self.SetPowerdownEnableAll():
            return -1

        # General enable (this is obsolete)
        self.FPGA.GeneralEnable.SetEnable(1)

        # Setup the sync generator block
        for Brd in BoardListCurrGpio:
            if self.FPGA.SysId.GetFwRevision() > 4:
                self.FPGA.SyncGenerator.SetTimestampResetValue(0xFFFFFFFF, Brd)
            self.FPGA.SyncGenerator.Reset(Brd)
            self.FPGA.SyncGenerator.SetEnable(1, Brd)

        # Start the acquisition by applying the sync clock, in common to all boards
        self.FPGA.ClockRefGenerator.SetEnable(1)

        return 0

    # Stop DAQ
    def StopDaq(self, FullStop=False, OnlyFpga=False):
        """
        Stop the DAQ.

        :return: Return status (a negative value means error).
        :rtype: int
        """
        if FullStop:
            self.FPGA.ClockRefGenerator.SetEnable(0)
            time.sleep(0.05)  # TODO: poll some registers to check that transmission is over
            self.FPGA.SyncGenerator.SetEnable(0)
            self.FPGA.GeneralEnable.SetEnable(0)
            self.FPGA.BoardControl.SetEnable(0)

        self.FPGA.DataPacketizer.SetEnable(0)
        if self.FPGA.Gpio is not None:
            self.FPGA.GpioControl.SetEnable(0)
            self.FPGA.GpioControl.SetCaptureEnable(0)
            self.FPGA.GpioControl.SetVirtualGpioEnable(0)
        Status = 0

        if not OnlyFpga:
            if self.SetPowerdownDisableAll():
                return -1
        if FullStop:
            if not OnlyFpga:
                for Brd in self.BoardList:
                    BrdIdx = self.FindBoardIdx(Brd)
                    CmdReply = self.Board[BrdIdx].StopDAQ(0)
                    Status = CmdReply.Status
                    if CmdReply.Status:
                        warnings.warn("Warning. StopDAQ - Brd: {}, Status: {}, Value: {}".format(Brd, CmdReply.Status,
                                                                                                 CmdReply.Value))
                        return -1

            Enabled = 0
            for Brd in range(0, len(self.Board)):
                Enabled |= self.FPGA.SyncGenerator.GetEnable(Brd)
            Enabled |= self.FPGA.GeneralEnable.GetEnable()

            if Enabled == 1 | Status < 0:
                return -1

        return 0

    @staticmethod
    def SetLogLevelDebug():
        log.setLevel(logging.DEBUG)

    @staticmethod
    def SetLogLevelInfo():
        log.setLevel(logging.INFO)

    @staticmethod
    def SetLogLevelWarning():
        log.setLevel(logging.WARNING)

    def SetLogToOutput(self):
        self.SetLogHandler(True)

    def SetLogToTmp(self):
        self.SetLogHandler(False)

    @staticmethod
    def SetLogHandler(LogToOutput):
        if LogToOutput:
            NewHandler = logging.StreamHandler(sys.stderr)
        else:
            NewHandler = logging.FileHandler('/var/log/bidaq', mode='a')
            # TODO: install new logging module, with file rotation
            # NewHandler = logging.RotatingFileHandler('/tmp/bidaq', mode='a', maxBytes=1 * 1024 * 1024, backupCount=10)
            NewFormatter = logging.Formatter(
                '%(asctime)-15s::%(levelname)s::%(filename)s::%(funcName)s::%(lineno)d::%(message)s')
            NewHandler.setFormatter(NewFormatter)
        for Handler in log.handlers[:]:
            log.removeHandler(Handler)
        log.addHandler(NewHandler)

    def TestBoards(self):
        for Brd in self.BoardList:
            BrdIdx = self.FindBoardIdx(Brd)
            Status = self.Board[BrdIdx].TestBoard(True)
            print("FINAL STATUS: ", Status)

    def GetInputVoltage(self, Board, Channel):
        if self.FPGA.SysId.GetFwRevision() >= 8:
            return (((self.FPGA.BoardControl.GetInData(Board, Channel) >> 8) & 0xFFFFFF) / 2 ** 23 - 1) * \
                   self.Board[Board].ADCFullRange * self.Board[Board].FilterGain
        else:
            log.warning("FPGA firmware v{} does not support GetInputVoltage".format(self.FPGA.SysId.GetFwRevision()))
            return None

    def GetInputValue(self, Board, Channel):
        if self.FPGA.SysId.GetFwRevision() >= 8:
            return (self.FPGA.BoardControl.GetInData(Board, Channel) >> 8) & 0xFFFFFF
        else:
            log.warning("FPGA firmware v{} does not support GetInputValue".format(self.FPGA.SysId.GetFwRevision()))
            return None

    def GetInputValueAll(self):
        InputValues = list()
        for Brd in self.BoardList:
            for Ch in range(0, 12):
                InputValues = InputValues + [self.GetInputValue(Brd, Ch)]
        return InputValues

    def FlashBoards(self, BinFile):

        self.Backplane.PortExpander.ResetBoards()
        time.sleep(0.1)

        Flash = FirmwareFlash.FirmwareFlash()
        Flash.DoFlash(BinFile)

        self.ResetBoards()

    def GetFPGAMonitorRegisters(self):
        """
        Get the FPGA monitoring registers.

        :return: Dictionary of several monitoring registers.
        :rtype: dict
        """

        MonitorDict = self.FPGA.GetMonitorRegisters()
        return MonitorDict

    def PrintFPGAMonitorRegisters(self):
        """
        Print the FPGA monitoring registers.
        """

        pprint.pprint(self.GetFPGAMonitorRegisters())

    def MonitorFPGAFifoFillLevels(self):
        """
        Continuously monitoring of the FIFO fill levels. Data is printed when a new and higher value is found in one of
        the FIFO's fill level registers. The function performs a polling, so the actual maximum fill level can be higher
        than the one displayed. To stop the function, press CTRL+C.
        """

        StoreMax = dict()

        while True:
            MonitorDict = self.GetFPGAMonitorRegisters()

            FifoList = ("FifoHpsMac", "FifoOutDataAdapter", "FifoOutData", "FifoTxMac", "FifoMiiConversion")
            for CurFifo in FifoList:
                if CurFifo not in StoreMax:
                    StoreMax[CurFifo] = MonitorDict[CurFifo]["FillLevel"]
                elif MonitorDict[CurFifo]["FillLevel"] > StoreMax[CurFifo]:
                    StoreMax[CurFifo] = MonitorDict[CurFifo]["FillLevel"]
                    print("New max - '{}': {}".format(CurFifo, StoreMax[CurFifo]))
                    pprint.pprint(StoreMax)

            for Brd in self.BoardList:
                for Ch in tuple(range(0, 12)):
                    KeyName = "FifoIn_Brd{}_Ch{}".format(Brd, Ch)
                    Value = MonitorDict["Board_{}".format(Brd)]["DataPacketizer"]["Channel_{}".format(Ch)][
                        "FIFOMaxFillLevel"]
                    if KeyName not in StoreMax:
                        StoreMax[KeyName] = Value
                    elif Value > StoreMax[KeyName]:
                        StoreMax[KeyName] = Value
                        print("New max - '{}': {}".format(KeyName, StoreMax[KeyName]))
                        pprint.pprint(StoreMax)


def __BoardsOptionsCallback(option, _opt, value, parser):
    setattr(parser.values, option.dest, list(map(int, value.split(','))))


def __MainFunction():
    Parser = optparse.OptionParser()

    Parser.set_usage("BiDAQ.py [options] start|stop|getboardlist|getboardnum")

    Parser.add_option("-c", "--crate", dest="Crate", type=int, default=None,
                      help="select crate number", metavar="CRATE")

    Parser.add_option("-H", "--half", dest="Half", type=int, default=None,
                      help="select crate half", metavar="HALF")

    Parser.add_option("-b", "--board-list", dest="Boards", type="string", default=None,
                      help="select list of boards (comma separated)", metavar="LIST", action='callback',
                      callback=__BoardsOptionsCallback)

    Parser.add_option("-f", "--filter-frequency", dest="FilterFreq", type=int, default=100,
                      help="select filter frequency", metavar="FREQ")

    Parser.add_option("-e", "--filter-enable", dest="FilterEnable", action='store_true',
                      help="select filter enable")

    Parser.add_option("-d", "--filter-disable", dest="FilterEnable", action='store_false',
                      help="select filter disable")

    Parser.set_defaults(FilterEnable=True)

    Parser.add_option("-I", "--input-connection", dest="InputConnection", type=int, default=0,
                      help="select filter input connection (0=conn, 1=gnd, 2=vrefp, 3=vrefn", metavar="VAL")

    Parser.add_option("-F", "--daq-frequency", dest="DaqFreq", type=int, default=1000,
                      help="select daq frequency", metavar="FREQ")

    # Parser.add_option("-m", "--mac-address", dest="MacAdrDst", type=int, default=0x123456789ABC,
    #                  help="select destination mac address", metavar="MAC")

    Parser.add_option("-i", "--ip-address", dest="IpAdrDst", type=int, default=0xC0A80104,
                      help="select destination ip address", metavar="IP")

    Parser.add_option("-p", "--port", dest="UdpPortDst", type=int, default=666,
                      help="select udp port", metavar="PORT")

    Parser.add_option("-s", "--adc-serial-readout", dest="ADCParallelReadout", action='store_false',
                      help="select adc serial readout")

    Parser.set_defaults(ADCParallelReadout=True)

    Parser.add_option("-t", "--timestamp-append", dest="DropTimestamp", action='store_false',
                      help="append timestamp to each sample")

    Parser.set_defaults(DropTimestamp=True)

    Parser.add_option("-m", "--master", dest="Master", action='store_true',
                      help="set fpga as master")

    Parser.set_defaults(Master=False)

    Parser.add_option("-G", "--gpio-enable", dest="Gpio", action='store_true',
                      help="enable gpio capture")

    Parser.set_defaults(Gpio=False)

    Parser.add_option("-V", "--virtual-gpio", dest="VirtualGpio", type=int, default=0,
                      help="select number of enabled virtual gpio ports", metavar="NUMBER")

    Parser.add_option("-S", "--samples-per-packet", dest="SamplesPerPacket", type=int, default=180,
                      help="select number of samples per packet", metavar="SAMPLES")

    Parser.add_option("-P", "--payload-type", dest="RTPPayloadType", type=int, default=20,
                      help="select the RTP payload type", metavar="PT")

    Parser.add_option("-v", action="store_true", dest="Verbose",
                      help="provide more information regarding operation")

    Parser.add_option("-D", action="store_true", dest="Debug",
                      help="provide debugging information")

    Parser.add_option("-l", action="store_true", dest="LogToOutput",
                      help="logging to standard output instead of /tmp")

    (Options, Args) = Parser.parse_args()

    # Check for sane arguments
    if len(Args) != 1:
        Parser.error("incorrect number of arguments")
    if str.lower(Args[0]) not in ('start', 'stop', 'getboardlist', 'getboardnum'):
        Parser.error("invalid argument (start|stop|getboardlist|getboardnum)")

    # Init class
    DaqTmp = BiDAQ(Crate=Options.Crate, Half=Options.Half, BoardList=Options.Boards, Verbose=Options.Verbose,
                   Debug=Options.Debug, LogToOutput=Options.LogToOutput)

    Status = -1

    with DaqTmp as Daq:

        if str.lower(Args[0]) == 'stop':

            logging.info("Stopping DAQ...")
            Status = Daq.StopDaq(FullStop=True)
            Daq.FPGA.SetSlave()
            if Status < 0:
                logging.error("Error: Can't stop DAQ")
            else:
                logging.info("Done")

        if str.lower(Args[0]) == 'start':

            BrdList = Daq.BoardList
            # Build channel config list according to input options. Apply the same settings to all channels
            CfgList = [
                [BrdList, [0], Options.InputConnection, Options.FilterEnable, Options.FilterFreq]
            ]
            Daq.SetChannelConfigList(CfgList)

            if Daq.FPGA.SysId.GetFwRevision() > 4:
                if Options.Master:
                    Daq.FPGA.SetMaster()
                else:
                    Daq.FPGA.SetSlave()

            if Options.Gpio:
                Daq.EnableGpio(Options.VirtualGpio, Options.ADCParallelReadout)

            logging.info("Starting DAQ...")
            Status = Daq.StartDaq(Options.IpAdrDst, Options.UdpPortDst, Options.DaqFreq,
                                  Options.SamplesPerPacket, Options.ADCParallelReadout, Options.DropTimestamp,
                                  Options.RTPPayloadType, None, Options.Gpio)
            if Status < 0:
                logging.error("Error: Can't start DAQ")
            else:
                logging.info("Done")

        if str.lower(Args[0]) == 'getboardlist':
            BoardNumList = list()
            for BrdIdx in range(len(Daq.Board)):
                BoardNumList.append(Daq.Board[BrdIdx].Board)
            Status = BoardNumList

        if str.lower(Args[0]) == 'getboardnum':
            Status = len(Daq.Board)

    # Required by MATLAB to check the return status
    print(Status)

    return Status


if __name__ == '__main__':
    sys.exit(__MainFunction())
