#!/usr/bin/python

class FpgaRegDict:

    # Dictionary creator
    @staticmethod
    def CreateDict(BoardsList=tuple(range(0, 8))):
        BiDAQ_control_0_bits = {
            "SPI_POL": (31, 31),
            "SPI_PHA": (30, 30),
            "SPI_CLK_DIV": (16, 29),
            "N_BIT": (10, 15),
            "CRC_EN": (9, 9),
            "SER_PAR": (8, 8),
            "N_SLAVE": (5, 7),
            "ID": (1, 4),
            "EN": (0, 0)}

        BiDAQ_control_1_bits = {
            "RDY_SAMPLE": (16, 31),
            "MISO_DELAY": (0, 15)}

        BiDAQ_control_2_bits = {
            "SSEL_HOLD": (16, 31),
            "RESET_HOLD": (0, 15)}

        pio_led_bits = {
            "LED0": (0, 0),
            "LED1": (1, 1),
            "LED2": (2, 2),
            "LED3": (3, 3)}

        pio_en_n_bits = {"EN_N": (0, 0)}

        sys_id_0_bits = {"SYSTEM_ID": (0, 31)}
        sys_id_1_bits = {"SYSTEM_ID_TIMESTAMP": (0, 31)}

        BiDAQ_packetizer_0_bits = {
            "PAYLOAD_HEADER": (12, 31),
            "RTP_PAYLOAD_TYPE": (4, 11),
            "DROP_TIMESTAMP": (2, 2),
            "DROP_ON_ERROR": (1, 1),
            "EN": (0, 0)}
        BiDAQ_packetizer_1_bits = {"PACKET_SAMPLES": (0, 31)}
        BiDAQ_packetizer_2_bits = {"RTP_SOURCE": (0, 31)}
        BiDAQ_packetizer_4_bits = {"PKT_CNT": (0, 31)}
        BiDAQ_packetizer_5_bits = {"DAT_CNT": (0, 31)}

        BiDAQ_packetizer_16_bits = dict()
        BiDAQ_packetizer_32_bits = dict()
        BiDAQ_packetizer_48_bits = dict()

        for i in range(0, 12):
            BiDAQ_packetizer_16_bits["BiDAQ_packetizer_{}_bits".format(16 + i)] = {
                "FIFO_FILL_LEVEL_{}".format(i): (0, 31)}
            BiDAQ_packetizer_32_bits["BiDAQ_packetizer_{}_bits".format(32 + i)] = {
                "MAX_FILL_LEVEL_{}".format(i): (0, 31)}
            BiDAQ_packetizer_48_bits["BiDAQ_packetizer_{}_bits".format(48 + i)] = {"CNT_DROPPED_{}".format(i): (0, 31)}

        BiDAQ_sync_generator_0_bits = {
            "RESET": (31, 31),
            "RESET_TIMESTAMP": (30, 30),
            "SYNC_DISABLE_VAL": (8, 8),
            "GENERATE_TIMESTAMP": (4, 4),
            "ENABLE": (0, 0)}
        BiDAQ_sync_generator_1_bits = {"DIVIDER": (0, 23)}
        BiDAQ_sync_generator_2_bits = {"PULSE_WIDTH": (0, 23)}
        BiDAQ_sync_generator_3_bits = {"TIMESTAMP_RESET_VALUE": (0, 31)}
        BiDAQ_sync_generator_4_bits = {"TIMESTAMP": (0, 31)}

        BiDAQ_sync_ref_generator_0_bits = {
            "EXT_CLK_REF_OUT_ENA": (3, 3),
            "INT_CLK_REF_IN_SEL": (2, 2),
            "EXT_CLK_REF_IN_ENA": (1, 1),
            "ENABLE": (0, 0)}
        BiDAQ_sync_ref_generator_1_bits = {"DIVIDER": (0, 7)}
        # BiDAQ_sync_ref_generator_2_bits = {}
        # BiDAQ_sync_ref_generator_3_bits = {}

        udp_payload_inserter_0_bits = {
            "ERR": (2, 2),
            "RUN": (1, 1),
            "EN": (0, 0)}
        udp_payload_inserter_1_bits = {"DEST_MAC_ADDRESS_MSB": (0, 31)}
        udp_payload_inserter_2_bits = {"DEST_MAC_ADDRESS_LSB": (0, 15)}
        udp_payload_inserter_3_bits = {"SOUR_MAC_ADDRESS_MSB": (0, 31)}
        udp_payload_inserter_4_bits = {"SOUR_MAC_ADDRESS_LSB": (0, 15)}
        udp_payload_inserter_5_bits = {"SOUR_IP_ADDRESS": (0, 31)}
        udp_payload_inserter_6_bits = {"DEST_IP_ADDRESS": (0, 31)}
        udp_payload_inserter_7_bits = {
            "DEST_UDP_PORT": (0, 15),
            "SOUR_UDP_PORT": (16, 31)}
        udp_payload_inserter_8_bits = {"PACKET_COUNT": (0, 31)}

        eth_mac_0_bits = {"REV": (0, 31)}
        eth_mac_1_bits = {"SCRATCH": (0, 31)}
        eth_mac_2_bits = {"COMMAND_CONFIG": (0, 31)}
        eth_mac_2_bits_detailed = {
            "TX_ENA": (0, 0),
            "RX_ENA": (1, 1),
            "XON_GEN": (2, 2),
            "ETH_SPEED": (3, 3),
            "PROMIS_EN": (4, 4),
            "PAD_EN": (5, 5),
            "CRC_FWD": (6, 6),
            "PAUSE_FWD": (7, 7),
            "PAUSE_IGNORE": (8, 8),
            "TX_ADDR_INS": (9, 9),
            "HD_ENA": (10, 10),
            "EXCESS_COL": (11, 11),
            "LATE_COL": (12, 12),
            "SW_RESET": (13, 13),
            "MHASH_SEL": (14, 14),
            "LOOP_ENA": (15, 15),
            "TX_ADDR_SEL": (16, 18),
            "MAGIC_ENA": (19, 19),
            "SLEEP": (20, 20),
            "WAKEUP": (21, 21),
            "XOFF_GEN": (22, 22),
            "CNTL_FRM_ENA": (23, 23),
            "NO_LGTH_CHECK": (24, 24),
            "ENA_10": (25, 25),
            "RX_ERR_DISC": (26, 26),
            "DISABLE_READ_TIMEOUT": (27, 27),
            "CNT_RESET": (31, 31)}
        eth_mac_3_bits = {"MAC_0": (0, 31)}
        eth_mac_4_bits = {"MAC_1": (0, 31)}
        eth_mac_5_bits = {"FRM_LENGTH": (0, 31)}
        eth_mac_6_bits = {"PAUSE_QUANTA": (0, 31)}
        eth_mac_7_bits = {"RX_SECTION_EMPTY": (0, 31)}
        eth_mac_8_bits = {"RX_SECTION_FULL": (0, 31)}
        eth_mac_9_bits = {"TX_SECTION_EMPTY": (0, 31)}
        eth_mac_10_bits = {"TX_SECTION_FULL": (0, 31)}
        eth_mac_11_bits = {"RX_ALMOST_EMPTY": (0, 31)}
        eth_mac_12_bits = {"RX_ALMOST_FULL": (0, 31)}
        eth_mac_13_bits = {"TX_ALMOST_EMPTY": (0, 31)}
        eth_mac_14_bits = {"TX_ALMOST_FULL": (0, 31)}
        eth_mac_15_bits = {"MDIO_ADDR0": (0, 4)}
        eth_mac_16_bits = {"MDIO_ADDR1": (0, 4)}
        eth_mac_17_bits = {"HOLDOFF_QUANT": (0, 15)}
        eth_mac_23_bits = {"TX_IPG_LENGTH": (0, 4)}
        eth_mac_24_bits = {"aMacID_H": (0, 31)}
        eth_mac_25_bits = {"aMacID_L": (0, 31)}
        eth_mac_26_bits = {"aFramesTransmittedOK": (0, 31)}
        eth_mac_27_bits = {"aFramesReceivedOK": (0, 31)}
        eth_mac_28_bits = {"aFrameCheckSequenceErrors": (0, 31)}
        eth_mac_29_bits = {"aAlignmentErrors": (0, 31)}
        eth_mac_30_bits = {"aOctetsTransmittedOK": (0, 31)}
        eth_mac_31_bits = {"aOctetsReceivedOK": (0, 31)}
        eth_mac_32_bits = {"aTxPAUSEMACCtrlFrames": (0, 31)}
        eth_mac_33_bits = {"aRxPAUSEMACCtrlFrames": (0, 31)}
        eth_mac_34_bits = {"ifInErrors": (0, 31)}
        eth_mac_35_bits = {"ifOutErrors": (0, 31)}
        eth_mac_36_bits = {"ifInUcastPkts": (0, 31)}
        eth_mac_37_bits = {"ifInMulticastPkts": (0, 31)}
        eth_mac_38_bits = {"ifInBroadcastPkts": (0, 31)}
        eth_mac_40_bits = {"ifOutUcastPkts": (0, 31)}
        eth_mac_41_bits = {"ifOutMulticastPkts": (0, 31)}
        eth_mac_42_bits = {"ifOutBroadcastPkts": (0, 31)}
        eth_mac_43_bits = {"etherStatsDropEvents": (0, 31)}
        eth_mac_44_bits = {"etherStatsOctets": (0, 31)}
        eth_mac_45_bits = {"etherStatsPkts": (0, 31)}
        eth_mac_46_bits = {"etherStatsUndersizePkts": (0, 31)}
        eth_mac_47_bits = {"etherStatsOversizePkts": (0, 31)}
        eth_mac_48_bits = {"etherStatsPkts64Octets": (0, 31)}
        eth_mac_49_bits = {"etherStatsPkts65to127Octets": (0, 31)}
        eth_mac_50_bits = {"etherStatsPkts128to255Octets": (0, 31)}
        eth_mac_51_bits = {"etherStatsPkts256to511Octets": (0, 31)}
        eth_mac_52_bits = {"etherStatsPkts512to1023Octets": (0, 31)}
        eth_mac_53_bits = {"etherStatsPkts1024to1518Octets": (0, 31)}
        eth_mac_54_bits = {"etherStatsPkts1519toXOctets": (0, 31)}
        eth_mac_55_bits = {"etherStatsJabbers": (0, 31)}
        eth_mac_56_bits = {"etherStatsFragments": (0, 31)}
        eth_mac_58_bits = {"TX_CMD_STAT": (0, 31)}
        eth_mac_58_bits_detailed = {
            "OMIT_CRC": (17, 17),
            "TX_SHIFT16": (18, 18)}
        eth_mac_59_bits = {"RX_CMD_STAT": (0, 31)}
        eth_mac_59_bits_detailed = {
            "RX_SHIFT16": (25, 25)}

        gmii_to_avalon_st_converter_0_bits = {"PKT_CNT": (0, 31)}
        gmii_to_avalon_st_converter_1_bits = {"DAT_CNT": (0, 31)}

        avalon_st_single_clock_fifo_0_bits = {"fill_level": (0, 23)}
        avalon_st_single_clock_fifo_2_bits = {"almost_full_threshold": (0, 31)}
        avalon_st_single_clock_fifo_3_bits = {"almost_empty_threshold": (0, 31)}
        avalon_st_single_clock_fifo_4_bits = {"cut_through_threshold": (0, 31)}
        avalon_st_single_clock_fifo_5_bits = {"drop_on_error": (0, 0)}

        hps_emac_interface_splitter_0_bits = {"MAC_SPEED": (0, 1)}

        LocalRegDict = {

            # pio_led
            "pio_led": (0x00001000, pio_led_bits),

            # pio_en_n
            "pio_en_n": (0x00002000, pio_en_n_bits),

            # sys_id
            "sys_id": {
                "sys_id_0": (0x00001010, sys_id_0_bits),
                "sys_id_1": (0x00001014, sys_id_1_bits)},

            # BiDAQ_sync_ref_generator
            "BiDAQ_sync_ref_generator": {
                "BiDAQ_sync_ref_generator_0": (0x00013000, BiDAQ_sync_ref_generator_0_bits),
                "BiDAQ_sync_ref_generator_1": (0x00013004, BiDAQ_sync_ref_generator_1_bits)},
            # "BiDAQ_sync_ref_generator_2":(0x00013008,BiDAQ_sync_ref_generator_2_bits),
            # "BiDAQ_sync_ref_generator_3":(0x0001300C,BiDAQ_sync_ref_generator_3_bits)},

            # udp_payload_inserter
            "udp_payload_inserter": {
                "udp_payload_inserter_0": (0x0020000, udp_payload_inserter_0_bits),
                "udp_payload_inserter_1": (0x0020004, udp_payload_inserter_1_bits),
                "udp_payload_inserter_2": (0x0020008, udp_payload_inserter_2_bits),
                "udp_payload_inserter_3": (0x002000C, udp_payload_inserter_3_bits),
                "udp_payload_inserter_4": (0x0020010, udp_payload_inserter_4_bits),
                "udp_payload_inserter_5": (0x0020014, udp_payload_inserter_5_bits),
                "udp_payload_inserter_6": (0x0020018, udp_payload_inserter_6_bits),
                "udp_payload_inserter_7": (0x002001C, udp_payload_inserter_7_bits),
                "udp_payload_inserter_8": (0x0020020, udp_payload_inserter_8_bits)},

            # eth_mac
            "eth_mac": {
                "eth_mac_0": (0x00030000, eth_mac_0_bits),
                "eth_mac_1": (0x00030004, eth_mac_1_bits),
                "eth_mac_2": (0x00030008, eth_mac_2_bits),
                "eth_mac_2_detailed": (0x00030008, eth_mac_2_bits_detailed),
                "eth_mac_3": (0x0003000C, eth_mac_3_bits),
                "eth_mac_4": (0x00030010, eth_mac_4_bits),
                "eth_mac_5": (0x00030014, eth_mac_5_bits),
                "eth_mac_6": (0x00030018, eth_mac_6_bits),
                "eth_mac_7": (0x0003001C, eth_mac_7_bits),
                "eth_mac_8": (0x00030020, eth_mac_8_bits),
                "eth_mac_9": (0x00030024, eth_mac_9_bits),
                "eth_mac_10": (0x00030028, eth_mac_10_bits),
                "eth_mac_11": (0x0003002C, eth_mac_11_bits),
                "eth_mac_12": (0x00030030, eth_mac_12_bits),
                "eth_mac_13": (0x00030034, eth_mac_13_bits),
                "eth_mac_14": (0x00030038, eth_mac_14_bits),
                "eth_mac_15": (0x0003003C, eth_mac_15_bits),
                "eth_mac_16": (0x00030040, eth_mac_16_bits),
                "eth_mac_17": (0x00030044, eth_mac_17_bits),
                "eth_mac_23": (0x0003005C, eth_mac_23_bits),
                "eth_mac_24": (0x00030060, eth_mac_24_bits),
                "eth_mac_25": (0x00030064, eth_mac_25_bits),
                "eth_mac_26": (0x00030068, eth_mac_26_bits),
                "eth_mac_27": (0x0003006C, eth_mac_27_bits),
                "eth_mac_28": (0x00030070, eth_mac_28_bits),
                "eth_mac_29": (0x00030074, eth_mac_29_bits),
                "eth_mac_30": (0x00030078, eth_mac_30_bits),
                "eth_mac_31": (0x0003007C, eth_mac_31_bits),
                "eth_mac_32": (0x00030080, eth_mac_32_bits),
                "eth_mac_33": (0x00030084, eth_mac_33_bits),
                "eth_mac_34": (0x00030088, eth_mac_34_bits),
                "eth_mac_35": (0x0003008C, eth_mac_35_bits),
                "eth_mac_36": (0x00030090, eth_mac_36_bits),
                "eth_mac_37": (0x00030094, eth_mac_37_bits),
                "eth_mac_38": (0x00030098, eth_mac_38_bits),
                "eth_mac_40": (0x000300A0, eth_mac_40_bits),
                "eth_mac_41": (0x000300A4, eth_mac_41_bits),
                "eth_mac_42": (0x000300A8, eth_mac_42_bits),
                "eth_mac_43": (0x000300AC, eth_mac_43_bits),
                "eth_mac_44": (0x000300B0, eth_mac_44_bits),
                "eth_mac_45": (0x000300B4, eth_mac_45_bits),
                "eth_mac_46": (0x000300B8, eth_mac_46_bits),
                "eth_mac_47": (0x000300BC, eth_mac_47_bits),
                "eth_mac_48": (0x000300C0, eth_mac_48_bits),
                "eth_mac_49": (0x000300C4, eth_mac_49_bits),
                "eth_mac_50": (0x000300C8, eth_mac_50_bits),
                "eth_mac_51": (0x000300CC, eth_mac_51_bits),
                "eth_mac_52": (0x000300D0, eth_mac_52_bits),
                "eth_mac_53": (0x000300D4, eth_mac_53_bits),
                "eth_mac_54": (0x000300D8, eth_mac_54_bits),
                "eth_mac_55": (0x000300DC, eth_mac_55_bits),
                "eth_mac_56": (0x000300E0, eth_mac_56_bits),
                "eth_mac_58": (0x000300E8, eth_mac_58_bits),
                "eth_mac_58_bits_detailed": (0x000300E8, eth_mac_58_bits_detailed),
                "eth_mac_59": (0x000300EC, eth_mac_59_bits),
                "eth_mac_59_bits_detailed": (0x000300EC, eth_mac_59_bits_detailed)},

            # gmii_to_avalon_st_converter
            "gmii_to_avalon_st_converter": {
                "gmii_to_avalon_st_converter_0": (0x00031000, gmii_to_avalon_st_converter_0_bits),
                "gmii_to_avalon_st_converter_1": (0x00031010, gmii_to_avalon_st_converter_1_bits)},

            # sc_fifo_hps_mac
            "sc_fifo_hps_mac": {
                "sc_fifo_hps_mac_0": (0x00032000, avalon_st_single_clock_fifo_0_bits),
                "sc_fifo_hps_mac_2": (0x00032008, avalon_st_single_clock_fifo_2_bits),
                "sc_fifo_hps_mac_3": (0x0003200C, avalon_st_single_clock_fifo_3_bits),
                "sc_fifo_hps_mac_4": (0x00032010, avalon_st_single_clock_fifo_4_bits),
                "sc_fifo_hps_mac_5": (0x00032014, avalon_st_single_clock_fifo_5_bits)},

            # fifo_adapter_data
            "fifo_adapter_data": {
                "fifo_adapter_data_0": (0x00028000, avalon_st_single_clock_fifo_0_bits),
                "fifo_adapter_data_2": (0x00028008, avalon_st_single_clock_fifo_2_bits),
                "fifo_adapter_data_3": (0x0002800C, avalon_st_single_clock_fifo_3_bits),
                "fifo_adapter_data_4": (0x00028010, avalon_st_single_clock_fifo_4_bits),
                "fifo_adapter_data_5": (0x00028014, avalon_st_single_clock_fifo_5_bits)},

            # sc_fifo_data
            "sc_fifo_data": {
                "sc_fifo_data_0": (0x00034000, avalon_st_single_clock_fifo_0_bits),
                "sc_fifo_data_2": (0x00034008, avalon_st_single_clock_fifo_2_bits),
                "sc_fifo_data_3": (0x0003400C, avalon_st_single_clock_fifo_3_bits),
                "sc_fifo_data_4": (0x00034010, avalon_st_single_clock_fifo_4_bits),
                "sc_fifo_data_5": (0x00034014, avalon_st_single_clock_fifo_5_bits)},

            # sc_fifo_tx_eth_tse
            "sc_fifo_tx_eth_tse": {
                "sc_fifo_tx_eth_tse_0": (0x00035000, avalon_st_single_clock_fifo_0_bits),
                "sc_fifo_tx_eth_tse_2": (0x00035008, avalon_st_single_clock_fifo_2_bits),
                "sc_fifo_tx_eth_tse_3": (0x0003500C, avalon_st_single_clock_fifo_3_bits),
                "sc_fifo_tx_eth_tse_4": (0x00035010, avalon_st_single_clock_fifo_4_bits),
                "sc_fifo_tx_eth_tse_5": (0x00035014, avalon_st_single_clock_fifo_5_bits)},

            # hps_emac_interface_splitter
            "hps_emac_interface_splitter": {
                "hps_emac_interface_splitter_0": (0x00033000, hps_emac_interface_splitter_0_bits)},

        }

        for i in BoardsList:
            # BiDAQ_control
            NewDict = {
                "BiDAQ_control_{}_0".format(i): (0x00010000 + 0x100 * i, BiDAQ_control_0_bits),
                "BiDAQ_control_{}_1".format(i): (0x00010004 + 0x100 * i, BiDAQ_control_1_bits),
                "BiDAQ_control_{}_2".format(i): (0x00010008 + 0x100 * i, BiDAQ_control_2_bits)}
            LocalRegDict["BiDAQ_control_{}".format(i)] = NewDict

            # BiDAQ_packetizer
            NewDict = {
                "BiDAQ_packetizer_{}_0".format(i): (0x00011000 + 0x100 * i, BiDAQ_packetizer_0_bits),
                "BiDAQ_packetizer_{}_1".format(i): (0x00011004 + 0x100 * i, BiDAQ_packetizer_1_bits),
                "BiDAQ_packetizer_{}_2".format(i): (0x00011008 + 0x100 * i, BiDAQ_packetizer_2_bits),
                "BiDAQ_packetizer_{}_4".format(i): (0x00011010 + 0x100 * i, BiDAQ_packetizer_4_bits),
                "BiDAQ_packetizer_{}_5".format(i): (0x00011014 + 0x100 * i, BiDAQ_packetizer_5_bits)}

            for j in range(0, 12):
                NewDict["BiDAQ_packetizer_{}_{}".format(i, 16 + j)] = (
                    0x00011040 + 0x100 * i + 0x004 * j,
                    BiDAQ_packetizer_16_bits["BiDAQ_packetizer_{}_bits".format(16 + j)])
                NewDict["BiDAQ_packetizer_{}_{}".format(i, 32 + j)] = (
                    0x00011080 + 0x100 * i + 0x004 * j,
                    BiDAQ_packetizer_32_bits["BiDAQ_packetizer_{}_bits".format(32 + j)])
                NewDict["BiDAQ_packetizer_{}_{}".format(i, 48 + j)] = (
                    0x000110C0 + 0x100 * i + 0x004 * j,
                    BiDAQ_packetizer_48_bits["BiDAQ_packetizer_{}_bits".format(48 + j)])

            LocalRegDict["BiDAQ_packetizer_{}".format(i)] = NewDict

            NewDict = {
                "BiDAQ_sync_generator_{}_0".format(i): (0x00012000 + 0x100 * i, BiDAQ_sync_generator_0_bits),
                "BiDAQ_sync_generator_{}_1".format(i): (0x00012004 + 0x100 * i, BiDAQ_sync_generator_1_bits),
                "BiDAQ_sync_generator_{}_2".format(i): (0x00012008 + 0x100 * i, BiDAQ_sync_generator_2_bits),
                "BiDAQ_sync_generator_{}_3".format(i): (0x0001200C + 0x100 * i, BiDAQ_sync_generator_3_bits),
                "BiDAQ_sync_generator_{}_4".format(i): (0x00012010 + 0x100 * i, BiDAQ_sync_generator_4_bits)}
            LocalRegDict["BiDAQ_sync_generator_{}".format(i)] = NewDict

        return LocalRegDict
