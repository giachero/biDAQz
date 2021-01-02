#!/usr/bin/python

from board import BiDAQBoard
from fpga import BiDAQFPGA
import warnings
import logging
import sys
import optparse

log = logging.getLogger("BiDAQ")


# noinspection DuplicatedCode
class BiDAQ:

    # Class constructor
    def __init__(self, Crate, BoardList=tuple(range(0, 8))):

        self.FPGA = BiDAQFPGA.BiDAQFPGA(BoardList)
        self.Board = list()
        for i in BoardList:
            self.Board.append(BiDAQBoard.BiDAQBoard(Crate, i))

    # Configure channels from a list
    def SetChannelConfigList(self, ConfigList):
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
                    Status, Value = self.Board[Brd].WriteFilterSettings(Channel, Freq, Enable, Ground)
                    if Status < 0:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        Status, Value)
                        )
        return Status

    # Configure channels from a dictionary
    def SetChannelConfigDict(self, ConfigDict):
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
                    Status, Value = self.Board[Brd].WriteFilterSettings(Channel, Freq, Enable, Ground)
                    if Status < 0:
                        warnings.warn(
                            "Warning. SetChannelConfig - Brd: {}, Ch: {}, Status: {}, Value: {}".format(Brd, Channel,
                                                                                                        Status, Value)
                        )
        return Status

    # Set DAQ frequency
    def SetFrequency(self, Frequency):

        SyncFreqDiv = round(500000 / (2 * Frequency))
        SyncFreq = 500000 / SyncFreqDiv
        AdcFreq = 0
        Status = 0

        for i in range(0, len(self.Board)):
            Status, AdcFreq = self.Board[i].WriteADCFrequency(0, SyncFreq * 1.04)
            AdcFreq = AdcFreq[0]
            log.debug(
                "Board[brd].WriteADCFrequency - brd: {}, Status: {}, AdcFreq: {}".format(i, Status, AdcFreq))
            if Status < 0:
                return Status, 0, 0

        self.FPGA.SyncGenerator.SetDivider(SyncFreqDiv)
        log.debug("FPGA.SetDivider - SyncFreq: {}, SyncFreqDiv: {}".format(SyncFreq / 2, SyncFreqDiv))
        return Status, SyncFreq, AdcFreq

    # Start DAQ
    def StartDaq(self, MacAdrDst, IpAdrDst, UdpPortDst, Frequency, AdcParallelReadout=1):

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

        self.FPGA.UdpStreamer.SetUdpStreamEnable(0)
        self.FPGA.UdpStreamer.AutoSetUdpStreamSourAddr()
        self.FPGA.UdpStreamer.SetUdpStreamDestMac(MacAdrDst)
        self.FPGA.UdpStreamer.SetUdpStreamDestIp(IpAdrDst)
        self.FPGA.UdpStreamer.SetUdpStreamDestPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamSourPort(UdpPortDst)
        self.FPGA.UdpStreamer.SetUdpStreamEnable(1)
        self.FPGA.BoardControl.SetADCMode(AdcParallelReadout)
        self.FPGA.BoardControl.SetEnable(1)
        self.FPGA.DataPacketizer.SetDropTimestamp(1)
        self.FPGA.DataPacketizer.SetPacketSamples(180)
        self.FPGA.DataPacketizer.SetRTPPayloadType(20)
        self.FPGA.DataPacketizer.SetPayloadHeader(0xBEEF)
        self.FPGA.DataPacketizer.SetEnable(1)
        self.FPGA.SyncGenerator.SetClockRefEnable(1)
        self.FPGA.SyncGenerator.Reset()
        self.FPGA.GeneralEnable.SetEnable(1)
        self.FPGA.SyncGenerator.SetEnable(1)

        return 0

    # Stop DAQ
    def StopDaq(self):

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


def BoardsOptionsCallback(option, _opt, value, parser):
    setattr(parser.values, option.dest, list(map(int, value.split(','))))


def main():
    Parser = optparse.OptionParser()

    Parser.set_usage("BiDAQ.py [options] start|stop")

    Parser.add_option("-c", "--crate", dest="Crate", type=int, default=0,
                      help="select crate number", metavar="CRATE")

    Parser.add_option("-b", "--board-list", dest="Boards", type="string", default=[0, 1],
                      help="select list of boards (comma separated)", metavar="LIST", action='callback',
                      callback=BoardsOptionsCallback)

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

    Parser.add_option("-m", "--mac-address", dest="MacAdrDst", type=int, default=0x123456789ABC,
                      help="select destination mac address", metavar="MAC")

    Parser.add_option("-i", "--ip-address", dest="IpAdrDst", type=int, default=0xC0A80104,
                      help="select destination ip address", metavar="IP")

    Parser.add_option("-p", "--port", dest="UdpPortDst", type=int, default=666,
                      help="select udp port", metavar="PORT")

    Parser.add_option("-s", "--adc-serial-readout", dest="ADCParallelReadout", action='store_false',
                      help="select adc serial readout")

    Parser.set_defaults(ADCParallelReadout=True)

    Parser.add_option("-v", action="store_true", dest="Verbose",
                      help="provide more information regarding operation")

    Parser.add_option("-D", action="store_true", dest="Debug",
                      help="provide debugging information")

    (Options, Args) = Parser.parse_args()

    # Check for sane arguments
    if len(Args) != 1:
        Parser.error("incorrect number of arguments")

    if str.lower(Args[0]) not in ('start', 'stop'):
        Parser.error("invalid argument")

    # if (Options.word_size != 1 and Options.word_size != 2
    #         and Options.word_size != 4):
    #     Parser.print_help()
    #     print("\nError: Invalid word size specified")
    #     return -1

    LogLevel = logging.WARNING
    if Options.Verbose:
        LogLevel = logging.INFO
    if Options.Debug:
        LogLevel = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=LogLevel)

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
        CfgList = [
            [Options.Boards, [0], Options.FilterGrounded, Options.FilterEnable, Options.FilterFreq]
        ]
        Daq.SetChannelConfigList(CfgList)

        logging.info("Starting DAQ...")
        Status = Daq.StartDaq(Options.MacAdrDst, Options.IpAdrDst, Options.UdpPortDst, Options.DaqFreq,
                              Options.ADCParallelReadout)
        if Status < 0:
            logging.error("Error: Can't start DAQ")
        else:
            logging.info("Done")

    print(Status)

    return Status


if __name__ == '__main__':
    sys.exit(main())
