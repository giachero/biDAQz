#!/usr/bin/python

from . import BiDAQFPGA


def main():
    FPGA = BiDAQFPGA.BiDAQFPGA(0)
    FPGA.TxMac.Initialize()


if __name__ == "__main__":
    main()
