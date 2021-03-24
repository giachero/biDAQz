#!/usr/bin/python

from board import BiDAQBoard
from fpga import BiDAQFPGA
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
    BiDAQ is the class to control the FPGA registers (through /dev/mem) and the BiDAQ boards (through CAN bus)
    """

    # Class constructor
    def __init__(self, Crate, BoardList=None):
        """
        BiDAQ class constructor.

        :param Crate: crate number - TODO: determine automatically using I2C (when using the full backplane)
        :type Crate: int
        :param BoardList: list of connected boards, if None, then the class will try to determine it automatically,
            using FPGA SysID register and querying boards with NOPs commands
        :type BoardList: list or tuple of integers
        """

        # Init the FPGA registers, if BoardList is None, the class will determine automatically the number of boards by
        # looking at the SysID register defined at build time
        self.FPGA = BiDAQFPGA.BiDAQFPGA(BoardList)

        # Retrieve the list
        self.BoardList = self.FPGA.BoardList

        # Scan the boards and check if they reply to a NOP command
        self.Board = list()
        for i in self.BoardList:
            self.Board.append(BiDAQBoard.BiDAQBoard(Crate, i))
            if self.Board[-1].NOP()[0] < 0:
                self.Board.pop()

    def FindBoardIdx(self, Brd):
        """
        Get board index from board number
        """

        for BrdIdx in range(len(self.Board)):
            if self.Board[BrdIdx].Board == Brd:
                return BrdIdx

        return None

    def SetChannelConfigList(self, ConfigList):
        """
        Configure channels using a list or tuple.

        :param ConfigList: channel configuration passed as a list of lists. Each element of the list must have 5
            elements: [Board, Channel, Ground, Enable, Frequency]. Board is a list of boards (counting from 0), e.g.
            [0,1]. Channel is a list of channels (0 means all channels of the board, 1-12), e.g. [1,2,3,4]. Ground is
            the setting for grounding the inputs (valid options are 0, 1, False or True). Enable is the setting to
            enable the Bessel filter (same options as before). Frequency is an int value for the Bessel filter cut-off
            frequency (valid values are from 24 to 2500). Example:
            [[[0,1],[1,2,3,4,5,6],True,True,24], [[0,1],[7,8,9,10,11,12],False,False,100]]
        :type ConfigList: list or tuple
        :return: return status (a negative value means error).
        :rtype: int
        """
        Status = 0
        for Line in ConfigList:
            for Brd in Line[0]:
                for Channel in Line[1]:
                    Ground = Line[2]
                    Enable = Line[3]
                    Freq = Line[4]
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

    def SetChannelConfigDict(self, ConfigDict):
        """
        Configure channels using a dictionary.

        :param ConfigDict: channel configuration is passed as a dictionary or list of dictionaries. Each key or element
            is a dictionary which must have specific keys: 'Board' - list of boards (counting from 0), e.g. [0,1],
            'Channel' - list of channels (1-12, 0 means all), 'Ground' - setting for grounding the inputs (valid options
            are 0, 1, False or True), 'Enable' - setting to enable the Bessel filter (same options as before), 'Freq' -
            int value for the Bessel filter cut-off frequency (valid values are from 24 to 2500).
        :type ConfigDict: dict
        :return: return status (a negative value means error).
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

        :param Frequency: requested DAQ sampling frequency.
        :type Frequency: int
        :return: a list with status (a negative value means error), synchronization signal frequency (at least twice the
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

        return Status, SyncFreq, AdcFreq

    # Start DAQ
    def StartDaq(self, IpAdrDst, UdpPortDst, Frequency, SamplesPerPacket=180, AdcParallelReadout=True,
                 DropTimestamp=True, RTPPayloadType=20):
        """
        Start the DAQ.

        :param IpAdrDst: destination IP address.
        :type IpAdrDst: int
        :param UdpPortDst: destination and source UDP ports.
        :type UdpPortDst: int
        :param Frequency: desired DAQ frequency.
        :type Frequency: int
        :param SamplesPerPacket: number of samples in each RTP packet.
        :type SamplesPerPacket: int
        :param AdcParallelReadout: set ADC parallel readout.
        :type AdcParallelReadout: bool
        :param DropTimestamp: drop timestamps from the output data stream.
        :type DropTimestamp: bool
        :param RTPPayloadType: set RTP payload type header field.
        :type RTPPayloadType: int
        :return: status (a negative value means error).
        :rtype: int
        """

        Status = self.StopDaq()
        if Status < 0:
            log.warning("Couldn't stop DAQ")
            return Status

        Status, SyncFreq, AdcFreq = self.SetFrequency(Frequency)
        if Status < 0:
            log.warning("Couldn't set DAQ frequency")
            return Status
        if AdcFreq < SyncFreq * 1.04:
            log.warning("DAQ freq is too high")
            return -1

        for Brd in range(0, len(self.Board)):
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
        # self.FPGA.UdpStreamer.SetUdpStreamDestMac(MacAdrDst)
        self.FPGA.UdpStreamer.SetUdpStreamDestIp(IpAdrDst)
        self.FPGA.UdpStreamer.AutoSetUdpStreamDestMac()
        self.FPGA.UdpStreamer.SetUdpStreamDestPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamSourPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamEnable(1)

        # Enable the SPI block
        self.FPGA.BoardControl.SetADCMode(AdcParallelReadout)
        self.FPGA.BoardControl.SetEnable(1)

        # Setup the RTP packet creator
        self.FPGA.DataPacketizer.SetDropTimestamp(DropTimestamp)
        self.FPGA.DataPacketizer.SetPacketSamples(SamplesPerPacket)
        self.FPGA.DataPacketizer.SetRTPPayloadType(RTPPayloadType)
        self.FPGA.DataPacketizer.SetPayloadHeader(self.FPGA.SyncGenerator.GetDivider(1) + 1)
        self.FPGA.DataPacketizer.SetEnable(1)

        # General enable (this is obsolete)
        self.FPGA.GeneralEnable.SetEnable(1)

        # Setup the sync generator block
        self.FPGA.SyncGenerator.SetTimestampResetValue(0xFFFFFFFF)
        self.FPGA.SyncGenerator.Reset()
        self.FPGA.SyncGenerator.SetEnable(1)

        # Start the acquisition by applying the sync clock, in common to all boards
        self.FPGA.SyncGenerator.SetClockRefEnable(1)

        return 0

    # Stop DAQ
    def StopDaq(self):
        """
        Stop the DAQ.

        :return: status (a negative value means error).
        :rtype: int
        """

        self.FPGA.SyncGenerator.SetClockRefEnable(0)
        time.sleep(0.05)  # TODO: poll some registers to check that transmission is over
        self.FPGA.SyncGenerator.SetEnable(0)
        self.FPGA.GeneralEnable.SetEnable(0)
        self.FPGA.BoardControl.SetEnable(0)
        self.FPGA.DataPacketizer.SetEnable(0)
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

        MonitorDict = self.FPGA.GetMonitorRegisters()
        return MonitorDict

    def PrintFPGAMonitorRegisters(self):

        pprint.pprint(self.GetFPGAMonitorRegisters())

    def MonitorFPGAFifoFillLevels(self):

        StoreMax = dict()

        while True:
            MonitorDict = self.GetFPGAMonitorRegisters()

            FifoList = ("FifoHpsMac", "FifoOutDataAdapter", "FifoOutData", "FifoTxMac")
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


def main():
    Parser = optparse.OptionParser()

    Parser.set_usage("BiDAQ.py [options] start|stop")

    Parser.add_option("-c", "--crate", dest="Crate", type=int, default=0,
                      help="select crate number", metavar="CRATE")

    Parser.add_option("-b", "--board-list", dest="Boards", type="string", default=[0, 1],
                      help="select list of boards (comma separated)", metavar="LIST", action='callback',
                      callback=__BoardsOptionsCallback)

    Parser.add_option("-f", "--filter-frequency", dest="FilterFreq", type=int, default=100,
                      help="select filter frequency", metavar="FREQ")

    Parser.add_option("-e", "--filter-enable", dest="FilterEnable", action='store_true',
                      help="select filter enable")

    Parser.add_option("-d", "--filter-disable", dest="FilterEnable", action='store_false',
                      help="select filter disable")

    Parser.set_defaults(FilterEnable=True)

    Parser.add_option("-g", "--filter-ground", dest="FilterGrounded", action='store_true',
                      help="select filter input ground")

    Parser.add_option("-C", "--filter-connected", dest="FilterGrounded", action='store_false',
                      help="select filter input connected")

    Parser.set_defaults(FilterGrounded=False)

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
    if str.lower(Args[0]) not in ('start', 'stop'):
        Parser.error("invalid argument (only start and stop are allowed)")

    LogLevel = logging.WARNING
    if Options.Verbose:
        LogLevel = logging.INFO
    if Options.Debug:
        LogLevel = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=LogLevel)

    # Init class
    Daq = BiDAQ(Options.Crate, Options.Boards)

    Status = -1

    if str.lower(Args[0]) == 'stop':

        logging.info("Stopping DAQ...")
        Status = Daq.StopDaq()
        if Status < 0:
            logging.error("Error: Can't stop DAQ")
        else:
            logging.info("Done")

    if str.lower(Args[0]) == 'start':

        # Build channel config list according to input options. Apply the same settings to all channels
        CfgList = [
            [Options.Boards, [0], Options.FilterGrounded, Options.FilterEnable, Options.FilterFreq]
        ]
        Daq.SetChannelConfigList(CfgList)

        logging.info("Starting DAQ...")
        Status = Daq.StartDaq(Options.IpAdrDst, Options.UdpPortDst, Options.DaqFreq,
                              Options.SamplesPerPacket, Options.ADCParallelReadout, Options.DropTimestamp,
                              Options.RTPPayloadType)
        if Status < 0:
            logging.error("Error: Can't start DAQ")
        else:
            logging.info("Done")

    # Required by MATLAB to check the return status
    print(Status)

    return Status


if __name__ == '__main__':
    sys.exit(main())
