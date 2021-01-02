#!/usr/bin/python

# import copy
import time

import BiDAQFPGA


def main():
    FPGA = BiDAQFPGA.BiDAQFPGA(2)

    Reg = "BiDAQ_control_0_0"
    Value = FPGA.LL.ReadRegister(Reg)
    print(Reg, "=", hex(Value))

    Reg = "BiDAQ_control_1_0"
    Value = FPGA.LL.ReadRegister(Reg)
    print(Reg, "=", hex(Value))

    RegisterList = ["BiDAQ_control_0_0", "BiDAQ_control_0_1", "BiDAQ_control_0_2", "udp_payload_inserter_0"]

    print(FPGA.LL.DumpRegisterList(RegisterList))

    Board = 0

    print("")
    FPGA.BoardControl.SetADCModeSerial(Board)
    print("BoardControl.GetADCMode", FPGA.BoardControl.GetADCMode(Board))
    FPGA.BoardControl.SetADCModeParallel(Board)
    print("BoardControl.GetADCMode", FPGA.BoardControl.GetADCMode(Board))
    FPGA.BoardControl.SetSPIClockDivider(2, Board)
    print("BoardControl.GetSPIClockDivider", FPGA.BoardControl.GetSPIClockDivider(Board))
    FPGA.BoardControl.SetSPIClockDivider(1, Board)
    print("BoardControl.GetSPIClockDivider", FPGA.BoardControl.GetSPIClockDivider(Board))
    FPGA.BoardControl.SetEnable(1, Board)
    print("BoardControl.GetEnable", FPGA.BoardControl.GetEnable(Board))
    FPGA.BoardControl.SetEnable(0, Board)
    print("BoardControl.GetEnable", FPGA.BoardControl.GetEnable(Board))

    print("")
    print("DataPacketizer.GetFIFOFillCount", FPGA.DataPacketizer.GetFIFOFillCount(Board))
    print("DataPacketizer.GetPacketCount", FPGA.DataPacketizer.GetPacketCount(Board))
    print("DataPacketizer.GetDataCount", FPGA.DataPacketizer.GetEnable(Board))
    print("DataPacketizer.GetFIFOMaxFillCount", FPGA.DataPacketizer.GetEnable(Board))
    print("DataPacketizer.GetDroppedDataCount", FPGA.DataPacketizer.GetEnable(Board))
    FPGA.DataPacketizer.SetEnable(1, Board)
    print("DataPacketizer.GetEnable", FPGA.DataPacketizer.GetEnable(Board))
    FPGA.DataPacketizer.SetEnable(0, Board)
    print("DataPacketizer.GetEnable", FPGA.DataPacketizer.GetEnable(Board))

    print("")
    FPGA.GeneralEnable.SetEnable(1)
    print("GeneralEnable.GetEnable", FPGA.GeneralEnable.GetEnable())
    FPGA.GeneralEnable.SetEnable(0)
    print("GeneralEnable.GetEnable", FPGA.GeneralEnable.GetEnable())

    print("")
    FPGA.SyncGenerator.SetEnable(0, Board)
    print("SyncGenerator.GetEnable", FPGA.SyncGenerator.GetEnable(Board))

    FPGA.SyncGenerator.SetReset(1, Board)
    print("SyncGenerator.GetReset", FPGA.SyncGenerator.GetReset(Board))
    FPGA.SyncGenerator.SetReset(0, Board)
    print("SyncGenerator.GetReset", FPGA.SyncGenerator.GetReset(Board))

    FPGA.SyncGenerator.SetTimestampReset(1, Board)
    print("SyncGenerator.GetTimestampReset", FPGA.SyncGenerator.GetTimestampReset(Board))
    FPGA.SyncGenerator.SetTimestampReset(0, Board)
    print("SyncGenerator.GetTimestampReset", FPGA.SyncGenerator.GetTimestampReset(Board))

    print("SyncGenerator.Reset", FPGA.SyncGenerator.Reset(Board))
    print("SyncGenerator.GetReset", FPGA.SyncGenerator.GetReset(Board))
    print("SyncGenerator.GetTimestampReset", FPGA.SyncGenerator.GetTimestampReset(Board))

    FPGA.SyncGenerator.SetDivider(15, Board)
    print("SyncGenerator.GetDivider", FPGA.SyncGenerator.GetDivider(Board))
    FPGA.SyncGenerator.SetDivider(9, Board)
    print("SyncGenerator.GetDivider", FPGA.SyncGenerator.GetDivider(Board))

    print("")
    FPGA.SyncGenerator.SetClockRefEnable(1)
    print("SyncGenerator.GetClockRefEnable", FPGA.SyncGenerator.GetClockRefEnable())

    FPGA.SyncGenerator.SetEnable(1, Board)
    print("SyncGenerator.GetEnable", FPGA.SyncGenerator.GetEnable(Board))

    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))
    time.sleep(0.1)
    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))

    FPGA.SyncGenerator.SetEnable(0, Board)
    print("SyncGenerator.GetEnable", FPGA.SyncGenerator.GetEnable(Board))

    FPGA.SyncGenerator.SetClockRefEnable(0)
    print("SyncGenerator.GetClockRefEnable", FPGA.SyncGenerator.GetClockRefEnable())

    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))
    time.sleep(0.1)
    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))

    print("SyncGenerator.Reset", FPGA.SyncGenerator.Reset(Board))

    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))
    time.sleep(0.1)
    print("SyncGenerator.GetTimestamp", FPGA.SyncGenerator.GetTimestamp(Board))

    print("")
    print("FifoHpsMac.GetCutThroughThr", FPGA.FifoHpsMac.GetCutThroughThr())
    print("FifoOutData.GetCutThroughThr", FPGA.FifoOutData.GetCutThroughThr())
    print("FifoTxMac.GetCutThroughThr", FPGA.FifoTxMac.GetCutThroughThr())
    FPGA.FifoHpsMac.SetCutThroughThr(10)
    FPGA.FifoOutData.SetCutThroughThr(10)
    FPGA.FifoTxMac.SetCutThroughThr(10)
    print("FifoHpsMac.GetCutThroughThr", FPGA.FifoHpsMac.GetCutThroughThr())
    print("FifoOutData.GetCutThroughThr", FPGA.FifoOutData.GetCutThroughThr())
    print("FifoTxMac.GetCutThroughThr", FPGA.FifoTxMac.GetCutThroughThr())

    RegBitList = [
        ["BiDAQ_control_0", "SPI_POL"],
        ["BiDAQ_control_0", "SPI_PHA"],
        ["BiDAQ_control_0", "SPI_CLK_DIV"],
        ["BiDAQ_control_0", "N_BIT"],
        ["BiDAQ_control_0", "CRC_EN"],
        ["BiDAQ_control_0", "SER_PAR"],
        ["BiDAQ_control_0", "N_SLAVE"],
        ["BiDAQ_control_0", "ID"],
        ["BiDAQ_control_0", "EN"],
        ["BiDAQ_control_0", "RDY_SAMPLE"],
        ["BiDAQ_control_0", "MISO_DELAY"],
        ["BiDAQ_control_0", "SSEL_HOLD"],
        ["BiDAQ_control_0", "RESET_HOLD"],
        ["eth_mac", "REV"],
        ["eth_mac", "SCRATCH"],
        ["eth_mac", "COMMAND_CONFIG"],
        ["eth_mac", "TX_ENA"],
        ["eth_mac", "RX_ENA"],
        ["eth_mac", "XON_GEN"],
        ["eth_mac", "ETH_SPEED"],
        ["eth_mac", "PROMIS_EN"],
        ["eth_mac", "PAD_EN"],
        ["eth_mac", "CRC_FWD"],
        ["eth_mac", "PAUSE_FWD"],
        ["eth_mac", "PAUSE_IGNORE"],
        ["eth_mac", "TX_ADDR_INS"],
        ["eth_mac", "HD_ENA"],
        ["eth_mac", "EXCESS_COL"],
        ["eth_mac", "LATE_COL"],
        ["eth_mac", "SW_RESET"],
        ["eth_mac", "MHASH_SEL"],
        ["eth_mac", "LOOP_ENA"],
        ["eth_mac", "TX_ADDR_SEL"],
        ["eth_mac", "MAGIC_ENA"],
        ["eth_mac", "SLEEP"],
        ["eth_mac", "WAKEUP"],
        ["eth_mac", "XOFF_GEN"],
        ["eth_mac", "CNTL_FRM_ENA"],
        ["eth_mac", "NO_LGTH_CHECK"],
        ["eth_mac", "ENA_10"],
        ["eth_mac", "RX_ERR_DISC"],
        ["eth_mac", "DISABLE_READ_TIMEOUT"],
        ["eth_mac", "CNT_RESET"],
        ["eth_mac", "MAC_0"],
        ["eth_mac", "MAC_1"],
        ["eth_mac", "FRM_LENGTH"],
        ["eth_mac", "PAUSE_QUANT"],
        ["eth_mac", "RX_SECTION_EMPTY"],
        ["eth_mac", "RX_SECTION_FULL"],
        ["eth_mac", "TX_SECTION_EMPTY"],
        ["eth_mac", "TX_SECTION_FULL"],
        ["eth_mac", "RX_ALMOST_EMPTY"],
        ["eth_mac", "RX_ALMOST_FULL"],
        ["eth_mac", "TX_ALMOST_EMPTY"],
        ["eth_mac", "TX_ALMOST_FULL"],
        ["eth_mac", "MDIO_ADDR0"],
        ["eth_mac", "MDIO_ADDR1"],
    ]

    print("\nRead default values")
    i = 0
    for RegBit in RegBitList:
        Value = FPGA.LL.ReadBits(RegBit[0], RegBit[1])
        RegBitList[i].append(Value)
        print(RegBit[0], "->", RegBit[1], "=", hex(Value))
        i += 1

    """print("\nWrite modified values")
    i = 0
    for RegBit in RegBitList:
        NewVal = RegBit[2] ^ 0xFFFFFFFF
        FPGA.LL.WriteBits(RegBit[0], RegBit[1], NewVal)
        print(RegBit[0], "->", RegBit[1], "=", hex(NewVal))
        i += 1

    print("\nRead modified values")
    i = 0
    RegBitListMod = copy.deepcopy(RegBitList)
    for RegBit in RegBitListMod:
        Value = FPGA.LL.ReadBits(RegBit[0], RegBit[1])
        RegBitListMod[i][2] = Value
        print(RegBit[0], "->", RegBit[1], "=", hex(Value), "-", RegBitListMod[i])
        i += 1

    print("\nWrite back original values")
    i = 0
    for RegBit in RegBitList:
        NewVal = RegBit[2]
        FPGA.LL.WriteBits(RegBit[0], RegBit[1], NewVal)
        print(RegBit[0], "->", RegBit[1], "=", hex(NewVal))
        i += 1

    print("\nRead original values")
    i = 0
    for RegBit in RegBitList:
        Value = FPGA.LL.ReadBits(RegBit[0], RegBit[1])
        RegBitList[i][2] = Value
        print(RegBit[0], "->", RegBit[1], "=", hex(Value), "-", RegBitList[i])
        i += 1

    for key, value in FPGA.LL.RegDict.RegDict.items():
        print(key, '--')
        # Again iterate over the nested dictionary
        #if isinstance(key, dict):
        #	for key2, value2 in value.items():
        #		print(key2, ' : ', value2)
        #else:
        #	print(key, ' : ', value)"""


"""FPGA.LL.WriteBits("BiDAQ_control_1","N_BIT",0x10)
value = c.Read_adr("BiDAQ_control_1_0")
print(hex(value),"ok2")

c.Write_adr("BiDAQ_control_1_0",0xC00183C3)
value=c.Read_Bits("BiDAQ_control_1","N_BIT")
print(hex(value),hex(value1),"ok3")

value1=c.Write_Bits("BiDAQ_control_1","N_BIT",0x10)
value=c.Read_adr("BiDAQ_control_1_0")
print(hex(value),hex(value1),"ok4")

value=c.Read_adr("BiDAQ_sync_generator_0_")
print(hex(value),"ok5")

dump_dict=c.dump(["BiDAQ_control_0_0", "BiDAQ_packetizer_0_1", "BiDAQ_sync_generator_0_2"])
print(dump_dict)"""

if __name__ == "__main__":
    main()
