#!/usr/bin/python

import random
# import time

import BiDAQBoard


def main():
    Err = 0

    for i in [0, 1]:

        print("\n-------- BOARD", i, "--------\n")

        Board0 = BiDAQBoard.BiDAQBoard(0, i)

        Board0.DebugFlag = False

        # print("Wake = \t\t\t",Board0.Wake())

        # Board0.SendData(Board0.CommandDict["CAN_CMD_FW_VER_READ"]["CommandByte"], 0)

        # Board0.SendCommand("NOP", 0, 0, None)
        # Board0.CheckReply ("NOP")
        # Board0.SendCommand("NOP", 0)

        # print(Board0.Restart())

        print("NOP =\t\t\t", Board0.NOP())

        Status, Val = Board0.ReadID()
        print("ReadID =\t\t", Status, Val)
        ID = random.randrange(2 ** 16)
        print("-- Random ID:", ID)
        print("WriteID =\t\t", Board0.WriteID(ID))
        Status, Val = Board0.ReadID()
        print("ReadID =\t\t", Status, Val)
        if Val[0] == ID:
            print("-- ID verified")
        else:
            print("-------- ERROR: ID not verified")
            Err = Err + 1

        print("ReadFWVersion =\t\t", Board0.ReadFWVersion())
        print("Blink =\t\t\t", Board0.Blink())

        Status, PD = Board0.ReadPowerdown()
        print("ReadPowerdown =\t\t", Status, PD)
        print("WritePowerdown =\t", Board0.WritePowerdown(not PD[0], 1))
        Status, Val = Board0.ReadPowerdown()
        print("ReadPowerdown =\t\t", Status, Val)
        if Val[0] == (not PD[0]):
            print("-- Powerdown verified")
        else:
            print("-------- ERROR: Powerdown not verified")
            Err = Err + 1
        print("WritePowerdown =\t", Board0.WritePowerdown(0, 1))

        print("WriteFilterEnable =\t", Board0.WriteFilterEnable(0, 1))
        print("ReadFilterEnable =\t", Board0.ReadFilterEnable(0))
        print("WriteFilterFrequency =\t", Board0.WriteFilterFrequency(0, 300))
        print("ReadFilterFrequency =\t", Board0.ReadFilterFrequency(1))
        print("WriteInputGrounded =\t", Board0.WriteInputGrounded(0, 1))
        print("ReadInputGrounded =\t", Board0.ReadInputGrounded(0))
        print("WriteFilterSettings =\t", Board0.WriteFilterSettings(0, 100, 1, 1))
        print("ReadTrimmer =\t\t", Board0.ReadTrimmer(1, 1))
        Status, Val = Board0.ReadTrimmer(1, 1)
        print("WriteTrimmer =\t\t", Board0.WriteTrimmer(1, 1, Val[0] - 1))
        print("ReadTrimmer =\t\t", Board0.ReadTrimmer(1, 1))
        print("WriteTrimmer =\t\t", Board0.WriteTrimmer(1, 1, Val[0]))
        print("ReadTrimmer =\t\t", Board0.ReadTrimmer(1, 1))
        print("ReadTrimmerForce =\t", Board0.ReadTrimmerForce(1, 1))
        print("WriteMeasEnable =\t", Board0.WriteMeasurementEnable(0, 1))
        print("ReadMeasEnable =\t", Board0.ReadMeasurementEnable(1))
        print("WriteMeasDuration =\t", Board0.WriteMeasurementDuration(0, 2))
        print("ReadMeasDuration =\t", Board0.ReadMeasurementDuration(1))
        print("WriteADCFrequency =\t", Board0.WriteADCFrequency(0, 5000, 0))
        print("ReadADCFrequency =\t", Board0.ReadADCFrequency(1))

        print("ReadADCRegister =\t", Board0.ReadADCRegister(1, 0x3B))
        Status, Val = Board0.ReadADCRegister(1, 0x3B)
        print("WriteADCRegister =\t", Board0.WriteADCRegister(1, 0x3B, Val[0] + 1))
        print("ReadADCRegister =\t", Board0.ReadADCRegister(1, 0x3B))
        print("WriteADCRegister =\t", Board0.WriteADCRegister(1, 0x3B, Val[0]))
        print("ReadADCRegister =\t", Board0.ReadADCRegister(1, 0x3B))
        print("WriteADCInputShorted =\t", Board0.WriteADCInputShorted(0, 0))
        print("ReadADCInputShorted =\t", Board0.ReadADCInputShorted(1))
        print("WriteADCInputBufEnable =", Board0.WriteADCInputBufferEnable(0, 0))
        print("ReadADCInputBufEnable =\t", Board0.ReadADCInputBufferEnable(1))
        print("ReadADCRefBufEnable =\t", Board0.ReadADCRefBufferEnable(1))
        print("WriteADCRefBufEnable =\t", Board0.WriteADCRefBufferEnable(0, 1))
        print("ReadADCRefBufEnable =\t", Board0.ReadADCRefBufferEnable(1))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 0))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 1))
        # print("WriteADCCalibration =\t", Board0.WriteADCCalibration(0, 0, 0x800000))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 0))
        # print("SaveADCCalibration =\t", Board0.SaveADCCalibration(0, 0))
        # print("WriteADCCalibration =\t", Board0.WriteADCCalibration(0, 0, 0x812345))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 0))
        # print("RecallADCCalibration =\t", Board0.RecallADCCalibration(0, 0))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 0))
        # print("AutoADCCalibration =\t", Board0.AutomaticADCCalibration(0))
        # print("ReadADCCalibration =\t", Board0.ReadADCCalibration(1, 0))

        # print("StartMeasurement =\t", Board0.StartMeasurement(0))
        # time.sleep(2.1)
        # print("StopMeasurement =\t", Board0.StopMeasurement(Channel))
        # for i in range(1,13):
        #     for j in range(0,7):
        #         print("ReadMeasurement("+str(i)+","+str(j)+") =\t", Board0.ReadMeasurement(i, j))
        # print(" =\t", Board0.ReadMeasurementData(Channel, Address, NData))
        # print("ReadADCConversion =\t", Board0.ReadADCConversion(1))
        print("WriteADCMode =\t\t", Board0.WriteADCMode(2))
        print("ReadADCMode =\t\t", Board0.ReadADCMode())
        # print("StartDAQ =\t\t", Board0.StartDAQ(0))
        # time.sleep(1)
        # print("StopDAQ =\t\t", Board0.StopDAQ(0))
        print("ReadTemperature =\t", Board0.ReadTemperature())
        for j in range(0, 8):
            print("ReadPowerSupply(" + str(j) + ") =\t", Board0.ReadPowerSupply(j))

        print("ReadTestpoint =\t\t", Board0.ReadTestpoint(1, 0))
        print("ReadTrimmerResistance =\t", Board0.ReadTrimmerResistance(1, 1))

        print("SaveSlot =\t\t", Board0.SaveSlot(1))

        print("LoadSlot =\t\t", Board0.LoadSlot(0))
        print("ReadFilterFrequency =\t", Board0.ReadFilterFrequency(1))

        print("LoadSlot =\t\t", Board0.LoadSlot(1))
        print("ReadFilterFrequency =\t", Board0.ReadFilterFrequency(1))

        print("ReadLockSlot =\t\t", Board0.ReadLockSlot(2))
        print("ToggleLockSlot =\t", Board0.ToggleLockSlot(2))
        print("ReadLockSlot =\t\t", Board0.ReadLockSlot(2))
        print("ToggleLockSlot =\t", Board0.ToggleLockSlot(2))
        print("ReadLockSlot =\t\t", Board0.ReadLockSlot(2))

        print("ReadUsedSlot =\t\t", Board0.ReadUsedSlot(1))
        print("SetUsedSlot =\t\t", Board0.SetUsedSlot(1))
        print("ReadUsedSlot =\t\t", Board0.ReadUsedSlot(1))
        print("SetUsedSlot =\t\t", Board0.SetUsedSlot(1))
        print("ReadUsedSlot =\t\t", Board0.ReadUsedSlot(1))

        print("ReadStartupSlot =\t", Board0.ReadStartupSlot())
        print("SetStartupSlot =\t", Board0.SetStartupSlot(1))
        print("ReadStartupSlot =\t", Board0.ReadStartupSlot())
        print("SetStartupSlot =\t", Board0.SetStartupSlot(0))

        print("LoadStartupSlot =\t", Board0.LoadStartupSlot())
        print("ReadFilterFrequency =\t", Board0.ReadFilterFrequency(1))

        print("LoadSlot =\t\t", Board0.LoadSlot(1))
        print("ReadFilterFrequency =\t", Board0.ReadFilterFrequency(1))

        Status, Val = Board0.ReadMemory(0xFFFF, 1)
        print("ReadMemory =\t\t", Status, Val)
        print("WriteMemory =\t\t", Board0.WriteMemory(0xFFFF, Val[0] - 1))
        print("ReadMemory =\t\t", Board0.ReadMemory(0xFFFF, 1))
        print("WriteMemory =\t\t", Board0.WriteMemory(0xFFFF, Val[0]))
        print("ReadMemory =\t\t", Board0.ReadMemory(0xFFFF, 1))

        # print("FormatMemory =\t\t", Board0.FormatMemory())

        print("ReadErrorCounter =\t", Board0.ReadErrorCounter())
        print("ResetErrorCounter =\t", Board0.ResetErrorCounter())
        print("ReadErrorCounter =\t", Board0.ReadErrorCounter())
        print("ReadErrorList =\t\t", Board0.ReadErrorList())
        print("ResetErrorList =\t", Board0.ResetErrorList())
        print("ReadErrorList =\t\t", Board0.ReadErrorList())
        print("ReadErrorMode =\t\t", Board0.ReadErrorMode())
        print("WriteErrorMode =\t", Board0.WriteErrorMode(0))


# t = time.time()
# print(Board1.FactoryReset())
# print("Elapsed time:",time.time() - t)

if __name__ == "__main__":
    main()
