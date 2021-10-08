#!/usr/bin/python

import logging

import can

from . import BiDAQCommands

log = logging.getLogger('BiDAQ.BiDAQBoard')


def _uint16_to_int16(Val):
    return (Val & 0x7FFF) - 0x8000 * ((Val & 0x8000) >> 15)


def _CheckADCNumber(ADCNumber, MinADC):
    if ADCNumber < MinADC or ADCNumber > 6:
        # raise Exception("Error. Wrong ADC number selected")
        return -1


def _CheckChannel(Channel):
    if Channel < 1 or Channel > 12:
        # raise Exception("Error. Wrong channel selected")
        return -1


class BiDAQBoard:
    DefaultTimeout = 0.1

    def __init__(self, crate, board):

        self.Crate = crate
        self.Board = board
        self.ID = int("0x00410000", 16) + (crate << 8) + (board << 4)
        self.CommandDict = BiDAQCommands.Import()
        self.CANBus = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)
        self.CANReader = can.BufferedReader()
        self.CANNotifier = can.Notifier(self.CANBus, [self.CANReader])
        self.LatestHwRev = -1

        self.CANBus.set_filters([{"can_id": self.ID, "can_mask": 0x1FFFFFF0, "extended": True}])

#        Status, Val = self.NOP()
#
#        if Status:
#            raise TimeoutError('Board at ID {} does not reply'.format(hex(self.ID)))

    def SendData(self, Command, Data, Channel=0, Timeout=DefaultTimeout, Queue=False):

        if Channel > 12 or Channel < 0:
            # raise Exception("Error. Wrong channel selected")
            return None

        # Convert input data to 4 bytes
        DataBytes = list(Data.to_bytes(4, 'big'))
        # Concatenate with command and status byte
        OutData = [Command] + DataBytes + [int(Queue)]
        # Build CAN message with data and extended ID
        OutMsg = can.Message(data=OutData)
        OutMsg.is_extended_id = True
        OutMsg.arbitration_id = self.ID + Channel

        log.debug("SendData - W: {}".format(OutMsg))

        # Send message
        self.CANBus.send(OutMsg)

        # Non-blocking case, return None
        if Timeout is None and not Queue:
            return None

        # Blocking-case, read incoming reply message
        InMsg = self.CANReader.get_message(Timeout)

        log.debug("SendData - R: {}".format(InMsg))

        return InMsg

    def SendCommand(self, CommandStr, Data, Channel=0, Timeout=DefaultTimeout, Queue=False):

        CommandStrExt = "CAN_CMD_" + CommandStr
        if CommandStrExt not in self.CommandDict:
            # raise ValueError("Command not found in command dictionary")
            return -1, None

        log.debug(
            "SendCommand - Cmd: {} - Data: {} - Ch {} - Timeout: {} - Queue: {}".format(CommandStrExt, Data, Channel,
                                                                                        Timeout, Queue))

        Status, Cnt = self.Wake()
        if Status:
            # raise Exception("The board can't be awaken or does not reply")
            return Status, Cnt

        InMsg = self.SendData(self.CommandDict[CommandStrExt]["CommandByte"], Data, Channel, Timeout)

        if InMsg is None:
            if Timeout is None:
                return None
            else:
                # raise Exception("Timeout. No reply to CAN bus command message")
                return Status, None

        Status, InData, Value = self.ParseInMsg(InMsg, CommandStrExt)

        log.debug("SendCommand - Status: {} - RcvData: {} - Return value: {}".format(Status, InData, Value))

        Status = self.CheckStatus(Status)

        if Status < 0:
            ErrString = "SendCommand - Command: {}".format(CommandStr)
            if Status == -1:
                log.warning(ErrString)
            if Status == -2:
                log.error(ErrString)

        return Status, Value

    def ParseInMsg(self, InMsg, CommandStr):

        Status = InMsg.data[5]

        InData = []
        Value = []
        for OutList in self.CommandDict[CommandStr]["OutputByteList"]:
            InData = [InMsg.data[i] for i in OutList]
            Value = Value + [int.from_bytes(bytes(InData), 'big')]

        return Status, InData, Value

    def CheckStatus(self, Status):

        if Status == self.CommandDict["CAN_CMD_NOT_IMPLEMENTED"]["CommandByte"]:
            # raise Exception("Error. Command not implemented")
            log.error("CheckStatus - Command not implemented")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_WRONG_CHANNEL"]["CommandByte"]:
            # raise Exception("Error. Wrong channel selected")
            log.error("CheckStatus - Wrong channel selected")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_WRONG_ARG"]["CommandByte"]:
            # raise Exception("Error. Wrong argument")
            log.error("CheckStatus - Wrong argument")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_UNKNOWN_CMD"]["CommandByte"]:
            # raise Exception("Error. Unknown command selected")
            log.error("CheckStatus - Unknown command selected")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_QUEUE_FULL"]["CommandByte"]:
            # raise Exception("Error. Command queue is full")
            log.error("CheckStatus - Command queue is full")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_ERROR"]["CommandByte"]:
            # raise Exception("Error. Command error")
            log.error("CheckStatus - Command error")
            Status = -2
        elif Status == self.CommandDict["CAN_CMD_BUSY"]["CommandByte"]:
            log.warning("CheckStatus - Board is busy")
            Status = -1
        elif Status == self.CommandDict["CAN_CMD_WARNING"]["CommandByte"]:
            log.warning("CheckStatus - Command warning")
            Status = -1
        return Status

    def CheckReply(self, CommandStr, Channel=0, Timeout=DefaultTimeout):

        CommandStrExt = "CAN_CMD_" + CommandStr
        if CommandStrExt not in self.CommandDict:
            # raise ValueError("Command not found in command dictionary")
            return -1, None

        InMsg = self.CANReader.get_message(Timeout)

        log.debug("CheckReply - {}".format(InMsg))

        if InMsg is None:
            # raise Exception("Timeout. No reply to CAN bus command message")
            return -1, None

        Command = InMsg.data[0]
        Status, InData, Value = self.ParseInMsg(InMsg, CommandStrExt)

        if Command != self.CommandDict[CommandStrExt]["CommandByte"]:
            # raise Exception("Error. Reply message comes from a different command")
            return -1, None

        if InMsg.arbitration_id != (self.ID + Channel):
            # raise Exception("Error. Reply message comes from a different ID")
            return -1, None

        log.debug("CheckReply - Status: {} - InData: {} - Value: {}".format(Status, InData, Value))

        Status = self.CheckStatus(Status)

        if Status < 0:
            ErrString = "CheckReply - Command: {}".format(CommandStr)
            if Status == -1:
                log.warning(ErrString)
            if Status == -2:
                log.error(ErrString)

        log.debug("CheckReply - Status: {}".format(Status))

        return Status, Value

    # Wake board from powerdown. The function waits a maximum of 0.1 s
    def Wake(self):

        Status = 0
        i = 0
        # Retry 10 times with 0.01 s timeout for each command
        for i in range(0, 10):
            # Send command without timeout
            self.SendData(self.CommandDict["CAN_CMD_NOP"]["CommandByte"], 0, 0, 0)
            # noinspection PyBroadException
            try:
                # Check the reply
                Status, Value = self.CheckReply("NOP", 0, 0.01)
                # If there is a reply, then break the cycle
                if Status == 0:
                    break
            except:
                # If there is an error, continue trying
                Status = -1
                pass

        log.debug("Wake - Status: {} - Cnt: {}".format(Status, i + 1))

        # Return status code and number of iterations
        return Status, i + 1

    # Initializations
    def InitBoard(self):
        Status, Value = self.ReadLatestHWRevision()
        if Status == 0:
            self.LatestHwRev = Value[0]
# Test commands to disable or enable reference buffers on the two boards
#            if self.LatestHwRev:
#                if self.Board == 1:
#                    self.WriteADCRefBufferEnable(0, 0)
#                #if self.Board == 0:
#                #    self.WriteADCRefBufferEnable(0, 1, 1)
        else:
            self.LatestHwRev = -1
        return 0

    # No OPeration (NOP) command
    def NOP(self, Queue=False):
        return self.SendCommand("NOP", 0, 0, self.DefaultTimeout, Queue)

    # Write ID to memory. The ID can be 16 bit maximum
    def WriteID(self, ID, Queue=False):
        return self.SendCommand("ID_WRITE", ID << 16, 0, self.DefaultTimeout, Queue)

    # Read ID from memory
    def ReadID(self, Queue=False):
        return self.SendCommand("ID_READ", 0, 0, self.DefaultTimeout, Queue)

    # Read FW version. Format: YYMMDDhhmm
    def ReadFWVersion(self, Queue=False):
        return self.SendCommand("FW_VER_READ", 0, 0, self.DefaultTimeout, Queue)

    # Read latest HW revision
    def ReadLatestHWRevision(self, Queue=False):
        return self.SendCommand("HW_REV_READ", 0, 0, self.DefaultTimeout, Queue)

    # Blink LEDs
    def Blink(self, Mode=0, Delay_ms=0, Period_ms=500, N=3, Queue=False):
        Value = (Mode << 24) + (int(Delay_ms / 10) << 16) + (int(Period_ms / 20) << 8) + N
        return self.SendCommand("BLINK", Value, 0, self.DefaultTimeout, Queue)

    # Restart the board. Command reply is quick, then the board takes some time to restart
    def Restart(self, Queue=False):
        return self.SendCommand("RESTART", 0, 0, self.DefaultTimeout, Queue)

    # Recalibrate the board. Command duration is 2.6 seconds
    def Recalibrate(self, Queue=False, Timeout=3):
        return self.SendCommand("RECALIBRATE", 0, 0, Timeout, Queue)

    # Enable or disable powerdown. The setting can be temporary or permanent
    def WritePowerdown(self, Powerdown, SaveInMemory=False, Queue=False):
        Value = (int(Powerdown) << 24) + ((int(SaveInMemory) & 1) << 16)
        return self.SendCommand("POWERDOWN_CONFIG", Value, 0, self.DefaultTimeout, Queue)

    # Read powerdown setting
    def ReadPowerdown(self, Queue=False):
        return self.SendCommand("POWERDOWN_READ", 0, 0, self.DefaultTimeout, Queue)

    # Reset the board to factory default, then restart the board. Command duration is 1.3 + restart time
    def FactoryReset(self, Queue=False, Timeout=2):
        return self.SendCommand("RESET_FACTORY", 0, 0, Timeout, Queue)

    # Enable the filter or bypass it
    def WriteFilterEnable(self, Channel, Enable, Queue=False):
        return self.SendCommand("FILTER_ENABLE_WRITE", int(Enable) << 24, Channel, self.DefaultTimeout, Queue)

    # Read filter enable setting
    def ReadFilterEnable(self, Channel, Queue=False):
        return self.SendCommand("FILTER_ENABLE_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write filter cut-off frequency
    def WriteFilterFrequency(self, Channel, Frequency, Queue=False):
        return self.SendCommand("FREQUENCY_WRITE", Frequency << 16, Channel, self.DefaultTimeout, Queue)

    # Read filter cut-off frequency
    def ReadFilterFrequency(self, Channel, Queue=False):
        if _CheckChannel(Channel):
            return -1
        return self.SendCommand("FREQUENCY_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Connect inputs or connect them to ground
    def WriteInputGrounded(self, Channel, Grounded, Queue=False):
        return self.SendCommand("INPUT_GROUND_WRITE", int(Grounded) << 24, Channel, self.DefaultTimeout, Queue)

    # Read input setting
    def ReadInputGrounded(self, Channel, Queue=False):
        return self.SendCommand("INPUT_GROUND_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write all the filter settings (cut-off frequency, filter enable, input connection)
    def WriteFilterSettings(self, Channel, Frequency, Enable, Grounded, Queue=False):
        Value = (Frequency << 16) + (int(Enable) << 8) + int(Grounded)
        return self.SendCommand("FREQUENCY_AND_ENABLE", Value, Channel, self.DefaultTimeout, Queue)

    # Write trimmer value
    def WriteTrimmer(self, Channel, TrimmerNumber, Value, Queue=False):
        Value = (TrimmerNumber << 24) + (Value << 8)
        return self.SendCommand("TRIMMER_WRITE", Value, Channel, self.DefaultTimeout, Queue)

    # Read trimmer value
    def ReadTrimmer(self, Channel, TrimmerNumber, Queue=False):
        if _CheckChannel(Channel):
            return -1
        return self.SendCommand("TRIMMER_READ", TrimmerNumber << 24, Channel, self.DefaultTimeout, Queue)

    # Read trimmer value from the trimmer and not from ucontroller RAM
    def ReadTrimmerForce(self, Channel, TrimmerNumber, Queue=False):
        if _CheckChannel(Channel):
            return -1
        return self.SendCommand("TRIMMER_READ_FORCE", TrimmerNumber << 24, Channel, self.DefaultTimeout, Queue)

    # Command duration is 0.42 s
    def LoadSlot(self, Slot, Timeout=0.5, Queue=False):
        return self.SendCommand("LOAD_SETTINGS", Slot << 24, 0, Timeout, Queue)

    def SaveSlot(self, Slot, Lock=False, Queue=False):
        Value = (Slot << 24) + ((int(Lock) & 1) << 16)
        return self.SendCommand("SAVE_SETTINGS", Value, 0, self.DefaultTimeout, Queue)

    def ToggleLockSlot(self, Slot, Queue=False):
        return self.SendCommand("SLOT_LOCK_WRITE", Slot << 24, 0, self.DefaultTimeout, Queue)

    def ReadLockSlot(self, Slot, Queue=False):
        return self.SendCommand("SLOT_LOCK_READ", Slot << 24, 0, self.DefaultTimeout, Queue)

    def SetUsedSlot(self, Slot, Queue=False):
        return self.SendCommand("SLOT_USED_WRITE", Slot << 24, 0, self.DefaultTimeout, Queue)

    def ReadUsedSlot(self, Slot, Queue=False):
        return self.SendCommand("SLOT_USED_READ", Slot << 24, 0, self.DefaultTimeout, Queue)

    def SetStartupSlot(self, Slot, Queue=False):
        return self.SendCommand("SLOT_STARTUP_WRITE", Slot << 24, 0, self.DefaultTimeout, Queue)

    def ReadStartupSlot(self, Queue=False):
        return self.SendCommand("SLOT_STARTUP_READ", 0, 0, self.DefaultTimeout, Queue)

    def LoadStartupSlot(self, Timeout=1, Queue=False):
        return self.SendCommand("LOAD_STARTUP_SETTINGS", 0, 0, Timeout, Queue)

    def WriteMemory(self, Address, Data, Queue=False):
        Value = (Address << 16) + ((Data & 0xFF) << 8)
        return self.SendCommand("MEMORY_WRITE", Value, 0, self.DefaultTimeout, Queue)

    def ReadMemory(self, Address, NBytes, Queue=False):
        Value = (Address << 16) + (NBytes << 8)
        return self.SendCommand("MEMORY_READ", Value, 0, self.DefaultTimeout, Queue)

    # Command duration is 2.2 s
    def FormatMemory(self, Timeout=2.5, Queue=False):
        return self.SendCommand("ERASE_ALL", 0, 0, Timeout, Queue)

    # Enable on-board DAQ-like measurements (average, RMS, min-max, etc)
    def WriteMeasurementEnable(self, Channel, Enable, Queue=False):
        return self.SendCommand("ADC_MEAS_EN_WRITE", int(Enable) << 24, Channel, self.DefaultTimeout, Queue)

    # Read on-board measurement enable
    def ReadMeasurementEnable(self, Channel, Queue=False):
        return self.SendCommand("ADC_MEAS_EN_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write on-board measurement duration. Max duration is 65.535 seconds
    def WriteMeasurementDuration(self, Channel, Duration, Queue=False):
        return self.SendCommand("ADC_ACQ_TIME_WRITE", int(Duration * 1000) << 16, Channel, self.DefaultTimeout, Queue)

    # Read on-board measurement duration
    def ReadMeasurementDuration(self, Channel, Queue=False):
        Status, Duration = self.SendCommand("ADC_ACQ_TIME_READ", 0, Channel, self.DefaultTimeout, Queue)
        return Status, [Duration[0] / 1000]

    # Write ADC frequency. Frequency is expressed in Hz. Bit 31 is the SING_CYC setting of ADC (default enabled)
    def WriteADCFrequency(self, Channel, Frequency, SingCycDisable=False, Queue=False):
        Value = int(Frequency * 1000) + (int(SingCycDisable) << 31)
        Status, Freq = self.SendCommand("ADC_FREQ_WRITE", Value, Channel, self.DefaultTimeout, Queue)
        return Status, [Freq[0] / 1000]

    # Read ADC frequency
    def ReadADCFrequency(self, Channel, Queue=False):
        Status, Freq = self.SendCommand("ADC_FREQ_READ", 0, Channel, self.DefaultTimeout, Queue)
        return Status, [Freq[0] / 1000]

    # Write ADC register. ADC number is 1-6 or 0 if all ADC are selected. Data is 24 bit maximum
    def WriteADCRegister(self, ADCNumber, Register, Data, Queue=False):
        if _CheckADCNumber(ADCNumber, 0):
            return
        Value = (Register << 24) + (Data & 0xFFFFFF)
        return self.SendCommand("ADC_REG_WRITE", Value, ADCNumber, self.DefaultTimeout, Queue)

    # Read ADC register. ADC number is 1-6
    def ReadADCRegister(self, ADCNumber, Register, Queue=False):
        if _CheckADCNumber(ADCNumber, 1):
            return
        return self.SendCommand("ADC_REG_READ", Register << 24, ADCNumber, self.DefaultTimeout, Queue)

    # Write ADC inputs short setting
    def WriteADCInputShorted(self, Channel, Shorted, Queue=False):
        return self.SendCommand("ADC_SHORT_INPUTS_WRITE", int(Shorted) << 24, Channel, self.DefaultTimeout, Queue)

    # Read ADC inputs short setting
    def ReadADCInputShorted(self, Channel, Queue=False):
        return self.SendCommand("ADC_SHORT_INPUTS_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write ADC input buffer enable
    def WriteADCInputBufferEnable(self, Channel, BufferEnable, Queue=False):
        return self.SendCommand("ADC_BUFFERS_WRITE", int(BufferEnable) << 24, Channel, self.DefaultTimeout, Queue)

    # Read ADC input buffer enable
    def ReadADCInputBufferEnable(self, Channel, Queue=False):
        return self.SendCommand("ADC_BUFFERS_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write ADC reference buffer enable
    def WriteADCRefBufferEnable(self, Channel, BufferEnable, OnlyPosBuffer=0, Queue=False):
        return self.SendCommand("ADC_REF_BUFFERS_WRITE", (int(BufferEnable) << 24) | int(OnlyPosBuffer) << 16, Channel,
                                self.DefaultTimeout, Queue)

    # Read ADC reference buffer enable
    def ReadADCRefBufferEnable(self, Channel, Queue=False):
        return self.SendCommand("ADC_REF_BUFFERS_READ", 0, Channel, self.DefaultTimeout, Queue)

    # Write ADC calibration data
    # Type can be 0 (offset ADC), 1 (gain ADC), 2 (offset memory), 3 (gain memory), 4 (gain byp memory)
    # Data is 24 bit
    def WriteADCCalibration(self, Channel, Type, Data, Queue=False):
        Value = (Type << 24) + (Data & 0xFFFFFF)
        return self.SendCommand("ADC_CALIBRATION_WRITE", Value, Channel, self.DefaultTimeout, Queue)

    # Read ADC calibration data
    # Type can be 0 (offset ADC), 1 (gain ADC), 2 (offset memory), 3 (gain memory), 4 (gain byp memory)
    def ReadADCCalibration(self, Channel, Type, Queue=False):
        return self.SendCommand("ADC_CALIBRATION_READ", Type << 24, Channel, self.DefaultTimeout, Queue)

    # Save ADC calibration data to memory
    # Type can be 0 (offset), 1 (gain), 2 (gain with filter disabled)
    def SaveADCCalibration(self, Channel, Type, Queue=False):
        return self.SendCommand("ADC_CALIBRATION_SAVE", Type << 24, Channel, self.DefaultTimeout, Queue)

    # Recall ADC calibration data from memory
    # Type can be 0 (offset), 1 (gain), 2 (gain with filter disabled)
    def RecallADCCalibration(self, Channel, Type, Queue=False):
        return self.SendCommand("ADC_CALIBRATION_RECALL", Type << 24, Channel, self.DefaultTimeout, Queue)

    # Perform ADC automatic offset calibration. Command duration is 2.65 s
    # The filter is connected, and the offset depends on the cut-off frequency
    def AutomaticADCCalibration(self, Channel, Queue=False, Timeout=3):
        return self.SendCommand("ADC_CALIBRATION_AUTO", 0, Channel, Timeout, Queue)

    def StartMeasurement(self, Channel, Queue=False):
        return self.SendCommand("ADC_START_MEAS", 0, Channel, self.DefaultTimeout, Queue)

    def StopMeasurement(self, Channel, Queue=False):
        return self.SendCommand("ADC_STOP_MEAS", 0, Channel, self.DefaultTimeout, Queue)

    # Read on-board measurement
    # Type can be average (0), RMS (1), max-min (2), status (3), number of samples (4), time (5), enable (6)
    def ReadMeasurement(self, Channel, Type, Queue=False):
        return self.SendCommand("ADC_READ_MEAS", Type << 24, Channel, self.DefaultTimeout, Queue)

    # Read on-board measurement raw data
    def ReadMeasurementData(self, Channel, Address, NData, Queue=False):
        Value = (Address << 16) + (NData & 0xFFFF)
        return self.SendCommand("ADC_READ_DATA", Value, Channel, self.DefaultTimeout, Queue)

    # Start continuous DAQ. AltSync is 1 for ALT_SYNC mode, or 0 for NORMAL_SYNC mode
    def StartDAQ(self, Channel, AltSync=True, Queue=False):
        return self.SendCommand("ADC_CONTINUOUS", (int(AltSync) & 1) << 24, Channel, self.DefaultTimeout, Queue)

    # Stop continuous DAQ
    def StopDAQ(self, Channel, Queue=False):
        return self.SendCommand("ADC_STOP", 0, Channel, self.DefaultTimeout, Queue)

    # Read single ADC conversion
    def ReadADCConversion(self, Channel, Queue=False):
        return self.SendCommand("ADC_SINGLE", 0, Channel, self.DefaultTimeout, Queue)

    # Write ADC mode. Mode is 0 (internal), 1 (external serial), 2 (external parallel)
    def WriteADCMode(self, Mode, Queue=False):
        return self.SendCommand("MODE_WRITE", Mode << 24, 0, self.DefaultTimeout, Queue)

    # Read ADC mode. Mode is 0 (internal), 1 (external serial), 2 (external parallel)
    def ReadADCMode(self, Queue=False):
        return self.SendCommand("MODE_READ", 0, 0, self.DefaultTimeout, Queue)

    # Read power supply with uController ADC
    # PowerSupply values:
    # 0 - External digital supply
    # 1 - Internal 5V digital supply
    # 2 - Internal 3.3V digital supply
    # 3 - Internal 5V ADC supply
    # 4 - External positive analog supply
    # 5 - External negative analog supply
    # 6 - Internal 12V analog supply
    # 7 - Internal -12V analog supply
    def ReadPowerSupply(self, PowerSupply, Queue=False):
        Status, Val = self.SendCommand("POWERSUPPLY_READ", PowerSupply << 24, 0, self.DefaultTimeout, Queue)
        return Status, [_uint16_to_int16(Val[0]) / 1000]

    # Read board temperature
    def ReadTemperature(self, Queue=False):
        Status, Val = self.SendCommand("TEMPERATURE_READ", 0, 0, self.DefaultTimeout, Queue)
        return Status, [_uint16_to_int16(Val[0]) / 100]

    # Read testpoint. Un valore di ritorno non è letto
    def ReadTestpoint(self, Channel, TestPoint, Queue=False, Timeout=1):
        return self.SendCommand("TESTPOINT_READ", TestPoint << 24, Channel, Timeout, Queue)

    # Read trimmer resistance. Una resistenza non è letta
    def ReadTrimmerResistance(self, Channel, Trimmer, Queue=False, Timeout=2):
        Status, Val = self.SendCommand("TRIMMER_RES_READ", Trimmer << 24, Channel, Timeout, Queue)
        return Status, [Val[0] / 500, Val[1] / 500]

    def ResetErrorCounter(self, Queue=False):
        return self.SendCommand("ERROR_CNT_RESET", 0, 0, self.DefaultTimeout, Queue)

    def ReadErrorCounter(self, Queue=False):
        return self.SendCommand("ERROR_CNT_READ", 0, 0, self.DefaultTimeout, Queue)

    def ResetErrorList(self, Queue=False):
        return self.SendCommand("ERROR_LIST_RESET", 0, 0, self.DefaultTimeout, Queue)

    def ReadErrorList(self, Queue=False):
        return self.SendCommand("ERROR_LIST_READ", 0, 0, self.DefaultTimeout, Queue)

    def WriteErrorMode(self, InstantMode, SaveInMemory=False, Queue=False):
        Value = (int(InstantMode) << 24) + ((int(SaveInMemory) & 1) << 16)
        return self.SendCommand("ERROR_INSTANT_MODE", Value, 0, self.DefaultTimeout, Queue)

    def ReadErrorMode(self, Queue=False):
        return self.SendCommand("ERROR_INSTANT_MODE_READ", 0, 0, self.DefaultTimeout, Queue)
