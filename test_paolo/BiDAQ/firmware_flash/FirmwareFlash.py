#!/usr/bin/python

import logging
import time
import can

log = logging.getLogger('BiDAQ.FirmwareFlash')

ENTER_BOOTLOADER = 0
GET_ID = 1
READ_ID = 2
ENTER_FLASH = 3
SELECT_SECTOR = 4
SEND_DATA = 5
SEND_CHECKSUM = 6
FLASH_STATUS = 7
EXIT_FLASH = 8

_StrToCommand = {
    'ENTER_BOOTLOADER': ENTER_BOOTLOADER,
    'GET_ID': GET_ID,
    'READ_ID': READ_ID,
    'ENTER_FLASH': ENTER_FLASH,
    'SELECT_SECTOR': SELECT_SECTOR,
    'SEND_DATA': SEND_DATA,
    'SEND_CHECKSUM': SEND_CHECKSUM,
    'FLASH_STATUS': FLASH_STATUS,
    'EXIT_FLASH': EXIT_FLASH,
}

_CommandToStr = {
    ENTER_BOOTLOADER: 'ENTER_BOOTLOADER',
    GET_ID: 'GET_ID',
    READ_ID: 'READ_ID',
    ENTER_FLASH: 'ENTER_FLASH',
    SELECT_SECTOR: 'SELECT_SECTOR',
    SEND_DATA: 'SEND_DATA',
    SEND_CHECKSUM: 'SEND_CHECKSUM',
    FLASH_STATUS: 'FLASH_STATUS',
    EXIT_FLASH: 'EXIT_FLASH',
}


class FirmwareFlash:
    DefaultTimeout = 0.01

    def __init__(self):

        self.ID = 0x100
        self.CANBus = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)
        self.CANReader = can.BufferedReader()
        self.CANNotifier = can.Notifier(self.CANBus, [self.CANReader])

    def WriteMessage(self, FlashCommand, OutData=None, Timeout=DefaultTimeout):

        if OutData is None:
            OutData = [0]

        if FlashCommand not in _StrToCommand:
            log.error("Error. Wrong command")
            return None
        ID = self.ID + _StrToCommand[FlashCommand]

        log.debug("WriteMessage - Cmd: {}, ID: 0x{:X}, Data: {}".format(FlashCommand, ID, OutData))

        OutMsg = can.Message(data=OutData)
        OutMsg.is_extended_id = True
        OutMsg.arbitration_id = ID
        OutMsg.timestamp = time.time()

        log.debug("WriteMessage - W: {}".format(OutMsg))

        # Send message
        self.CANBus.send(OutMsg)

        # Non-blocking case, return None
        if Timeout == 0:
            return None

        # Blocking-case, read incoming reply message
        StartTime = time.time()
        InMsg = list()
        while (time.time() - StartTime) < Timeout:
            InMsgTmp = self.CANReader.get_message(Timeout/20)
            if InMsgTmp is not None:
                log.debug("WriteMessage - R: {}".format(InMsgTmp))
                InMsg = InMsg + [InMsgTmp]

        return InMsg

    def DoFlash(self, BinFile):

        log.info("DoFlash - Entering bootloader mode")
        self.WriteMessage('ENTER_BOOTLOADER', Timeout=0)
        log.info("DoFlash - Entered bootloader mode")

        log.info("DoFlash - Reading IDs of microcontrollers in bootloader mode")
        IDList = list()
        InMsg = self.WriteMessage('GET_ID')
        for i in range(len(InMsg)):
            InDataTmp = int.from_bytes(bytes(InMsg[i].data), 'big') >> 32
            Cmd = _CommandToStr[InMsg[i].arbitration_id - 0x110]
            log.info("DoFlash - Command: {}, ID: 0x{:X}".format(Cmd, InDataTmp))
            IDList = IDList + [InDataTmp]

        log.info("DoFlash - Selecting microcontrollers for programming")
        for i in range(len(InMsg)):
            self.WriteMessage('ENTER_FLASH', InMsg[i].data, Timeout=0)
            log.info("DoFlash - Selected ID: 0x{:X}".format(IDList[i]))

        Sector = 0

        with open(BinFile, "rb", buffering=4096) as File:

            while True:

                SectorData = File.read(4096)
                if not SectorData:
                    break

                SectorData = list(SectorData)

                for CntRetry in range(10):

                    log.info("DoFlash - Selecting sector {}".format(Sector))
                    self.WriteMessage('SELECT_SECTOR', [Sector], Timeout=0)
                    log.info("DoFlash - Selected sector {}".format(Sector))

                    Checksum = [0] * 4

                    log.info("DoFlash - Writing sector")
                    for Chunk in range(512):  # 4096/8
                        WriteData = [0xFF] * 8
                        WriteDataNew = SectorData[(8 * Chunk):(8 * (Chunk + 1))]
                        WriteData[0:len(WriteDataNew)] = WriteDataNew
                        for i in range(4):
                            Checksum[i] += (Chunk + 1) * (WriteData[2*i] | (WriteData[2*i+1] * 2**8))
                            if Checksum[i] > (2**32 - 1):
                                Checksum[i] -= 2**32
                        self.WriteMessage('SEND_DATA', WriteData, Timeout=0)
                    log.info("DoFlash - Finished writing sector")

                    ChecksumH = Checksum[0] ^ Checksum[3]
                    ChecksumL = Checksum[1] ^ Checksum[2]

                    WriteData = list(int.to_bytes(ChecksumH, 4, 'little')) + list(int.to_bytes(ChecksumL, 4, 'little'))

                    log.info("DoFlash - Sending checksum {}".format(WriteData))
                    self.WriteMessage('SEND_CHECKSUM', WriteData)

                    StartTime = time.time()
                    AllReplied = False
                    IDListCheck = IDList[:]
                    while (time.time() - StartTime) < 5:
                        InMsg = self.CANReader.get_message(0.001)
                        if InMsg is None:
                            continue

                        InData = int.from_bytes(bytes(InMsg.data), 'big')
                        IDReply = InData >> 32
                        Cmd = _CommandToStr[InMsg.arbitration_id - 0x110]
                        Status = (InData >> 24) & 0xFF
                        if Status == 0:
                            StatusStr = "WRONG_HASH"
                        elif Status == 1:
                            StatusStr = "FLASH_ERROR"
                        elif Status == 3:
                            StatusStr = "OK"
                        else:
                            StatusStr = "UNKNOWN_STATUS"
                        log.info("DoFlash - Reply from ID: 0x{:X}, Cmd: {}, Status: {}".format(IDReply, Cmd, StatusStr))

                        IDListCheck = list(filter(lambda a: a != IDReply, IDListCheck))
                        if not IDListCheck:
                            AllReplied = True
                            break

                    if AllReplied:
                        break

                if AllReplied:
                    log.info("DoFlash - Sector {} flashed correctly on all boards".format(Sector))
                if not AllReplied:
                    log.info("DoFlash - Cannot write sector {} on following IDs: {}".format(Sector, IDListCheck))

                Sector += 1

        log.info("DoFlash - Exiting programming")
        self.WriteMessage('EXIT_FLASH', Timeout=0)
        log.info("DoFlash - Programming terminated")
