#!/usr/bin/python

from board import BiDAQBoard
from fpga import BiDAQFPGA
from backplane import BiDAQBackplane

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

    def __init__(self, Crate=None, Half=None, BoardList=None):
        """
        :param Crate: Crate number. If None, it is read automatically using the I2C port expander.
        :type Crate: int
        :param Half: Backplane half. If None, it is read automatically using the I2C port expander.
        :type Half: int
        :param BoardList: List of connected boards. If None, the class will try to determine it automatically,
            using FPGA SysID register (to read how many blocks are instantiated) and querying boards with NOP commands
            through CAN bus.
        :type BoardList: list or tuple of integers
        """

        # logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        # Init the FPGA registers, if BoardList is None, the class will determine automatically the number of boards by
        # looking at the SysID register defined at build time
        self.FPGA = BiDAQFPGA.BiDAQFPGA(BoardList)

        # Init the backplane class
        if self.FPGA.SysId.GetFwRevision() > 4:
            self.Backplane = BiDAQBackplane.BiDAQBackplane()

        if Crate is None:
            try:
                self.Crate = self.Backplane.Crate
            except AttributeError:
                self.Crate = 0
        else:
            self.Crate = Crate

        if Half is None:
            try:
                self.Half = self.Backplane.Half
            except AttributeError:
                self.Half = 0
        else:
            self.Half = Half

        # Scan the boards and check if they reply to a NOP command
        self.Board, self.BoardList = self.InitBoards()

        self.FPGA.InitRtpSourceIds(0xB1DAC, self.Crate, self.Half)

    def InitBoards(self):
        """
        Initialize :class:`board.BiDAQBoard` class by checking that the boards are replying correctly. The function
        uses *BoardList* instance variable as the list of boards to scan.

        :return: A list of :class:`board.BiDAQBoard` classes and the new *BoardList*.
        :rtype: list of :class:`board.BiDAQBoard`, list of integers
        """
        Board = list()
        BoardList = self.FPGA.BoardList.copy()

        logging.info("Initializing BiDAQ boards")
        logging.info("Starting BoardList: {}".format(BoardList))

        for CurrentBoard in self.FPGA.BoardList:
            Board.append(BiDAQBoard.BiDAQBoard(self.Crate & 0xF, CurrentBoard + 8*self.Half))
            if Board[-1].NOP()[0] < 0:
                Board.pop()
                BoardList.remove(CurrentBoard)
            else:
                Board[-1].InitBoard()
        self.BoardList = BoardList

        if len(BoardList) is 0:
            logging.warning("No boards found during initialization")

        logging.info("Final BoardList: {}".format(BoardList))

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
            if self.Board[BrdIdx].Board == Brd:
                return BrdIdx

        return None

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
                    Status, Value = self.Board[BrdIdx].WriteFilterSettings(Channel, Freq, Enable, Input)
                    if Status < 0:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        Status, Value)
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
                    Status, Value = self.Board[BrdIdx].WriteFilterSettings(Channel, Freq, Enable, Ground)
                    if Status < 0:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        Status, Value)
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
            Status, AdcFreq = self.Board[i].WriteADCFrequency(0, SyncFreq * 1.04)
            AdcFreq = AdcFreq[0]
            log.debug(
                "Board[brd].WriteADCFrequency - brd: {}, Status: {}, AdcFreq: {}".format(i, Status, AdcFreq))
            if Status < 0:
                return Status, 0, 0

        # Set the same divider on all the boards
        self.FPGA.SyncGenerator.SetDivider(SyncFreqDiv)
        log.debug("FPGA.SetDivider - SyncFreq: {}, SyncFreqDiv: {}".format(SyncFreq / 2, SyncFreqDiv))

#        if self.FPGA.Gpio is not None:
#            self.FPGA.SyncGenerator.SetDivider(SyncFreqDiv * 2, self.FPGA.Gpio)

        return Status, SyncFreq, AdcFreq

    def EnableGpio(self, VirtualGpioNumber=0):
        """
        Enable GPIO capture. The optional argument allow to enable also up to 7 24-bit virtual GPIOs.

        :param VirtualGpioNumber: Number of virtual GPIOs to be enabled (0-7).
        :type VirtualGpioNumber: int
        """

        self.FPGA.GpioControl.SetCaptureEnable(1)
        self.FPGA.GpioControl.SetEnable(1)
        for i in list(range(1, VirtualGpioNumber + 1)):
            self.FPGA.GpioControl.SetVirtualGpioEnable(1, i)

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

        # TODO: check that DAQ is not running
#        Status = self.StopDaq()
#        if Status < 0:
#            log.warning("Couldn't stop DAQ")
#            return Status

        Status, SyncFreq, AdcFreq = self.SetFrequency(Frequency)
        if Status < 0:
            log.warning("Couldn't set DAQ frequency")
            return Status
        if AdcFreq < SyncFreq * 1.04:
            log.warning("DAQ freq is too high (AdcFreq: {}, SyncFreq: {})".format(AdcFreq, SyncFreq))
            return -1

        if BoardList is None:
            BoardListCurr = list(range(len(self.Board)))
        else:
            BoardListCurr = BoardList

        for Brd in BoardListCurr:
            Status, Value = self.Board[Brd].WriteADCMode(AdcParallelReadout + 1)
            if Status < 0:
                log.warning("Warning. WriteADCMode - Brd: {}, Status: {}, Value: {}".format(Brd, Status, Value))
                return Status
            Status, Value = self.Board[Brd].StartDAQ(0)
            if Status < 0:
                log.warning("Warning. StartDAQ - Brd: {}, Status: {}, Value: {}".format(Brd, Status, Value))
                return Status

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
                Status, LatestHWRevision = self.Board[Brd].ReadLatestHWRevision()
                if Status < 0:
                    log.warning("Warning. ReadLatestHWRevision - Brd: {}, Status: {}".format(Brd, Status))
                    return Status
                Status, FilterEnable = self.Board[Brd].ReadFilterEnable(1)
                if Status < 0:
                    log.warning("Warning. ReadFilterEnable - Brd: {}, Status: {}".format(Brd, Status))
                    return Status
                RTPPayloadTypeTmp = RTPPayloadTypeTmp | (LatestHWRevision[0] << 1) | (FilterEnable[0])

            self.FPGA.DataPacketizer.SetRTPPayloadType(RTPPayloadTypeTmp, True, Brd)
            self.FPGA.DataPacketizer.SetPayloadHeader(self.FPGA.SyncGenerator.GetDivider(Brd), Brd)
            self.FPGA.DataPacketizer.SetEnable(1, Brd)

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
    def StopDaq(self):
        """
        Stop the DAQ.

        :return: Return status (a negative value means error).
        :rtype: int
        """

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

        for Brd in range(0, len(self.Board)):
            Status, Value = self.Board[Brd].StopDAQ(0)
            if Status < 0:
                warnings.warn("Warning. StopDAQ - Brd: {}, Status: {}, Value: {}".format(Brd, Status, Value))
                return -1

        Enabled = 0
        for Brd in range(0, len(self.Board)):
            Enabled |= self.FPGA.SyncGenerator.GetEnable(Brd)
        Enabled |= self.FPGA.GeneralEnable.GetEnable()

        if Enabled == 1 | Status < 0:
            return -1

        return 0

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

    (Options, Args) = Parser.parse_args()

    # Check for sane arguments
    if len(Args) != 1:
        Parser.error("incorrect number of arguments")
    if str.lower(Args[0]) not in ('start', 'stop', 'getboardlist', 'getboardnum'):
        Parser.error("invalid argument (start|stop|getboardlist|getboardnum)")

    LogLevel = logging.WARNING
    if Options.Verbose:
        LogLevel = logging.INFO
    if Options.Debug:
        LogLevel = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=LogLevel)

    # Init class
    Daq = BiDAQ(Options.Crate, Options.Half, Options.Boards)

    Status = -1

    if str.lower(Args[0]) == 'stop':

        logging.info("Stopping DAQ...")
        Status = Daq.StopDaq()
        if Status < 0:
            logging.error("Error: Can't stop DAQ")
        else:
            logging.info("Done")

    if str.lower(Args[0]) == 'start':

        BrdList = Daq.BoardList
        # Build channel config list according to input options. Apply the same settings to all channels
        CfgList = [
            [[x+8*Daq.Half for x in BrdList], [0], Options.InputConnection, Options.FilterEnable, Options.FilterFreq]
        ]
        Daq.SetChannelConfigList(CfgList)

        if Daq.FPGA.SysId.GetFwRevision() > 4:
            if Options.Master:
                Daq.FPGA.SetMaster()
            else:
                Daq.FPGA.SetSlave()

        if Options.Gpio:
            Daq.EnableGpio(Options.VirtualGpio)

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
