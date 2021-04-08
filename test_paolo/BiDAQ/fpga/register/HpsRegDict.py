#!/usr/bin/python

class HpsRegDict:

    # Dictionary creator
    @staticmethod
    def CreateDict():

        hps_pll_user1_clock_divider_bits = {"DIVIDER": (0, 8)}
        hps_pll_user1_clock_enable_bits = {"ENABLE": (7, 7)}

        hps_pll_peripheral_vco_bits = {
            "DENOMINATOR": (16, 21),
            "NUMERATOR": (3, 15)}

        LocalRegDict = {

            # hps_pll_user1_clock
            "hps_pll_user1_clock": {
                "hps_pll_user1_clock_divider": (0x00D0409C, hps_pll_user1_clock_divider_bits),
                "hps_pll_user1_clock_enable":  (0x00D040A0, hps_pll_user1_clock_enable_bits)},

            # hps_pll_peripheral_vco
            "hps_pll_peripheral_vco": (0x00D04080, hps_pll_peripheral_vco_bits),

        }

        return LocalRegDict
