#!/usr/bin/python

import BiDAQ
import sys


def __MainFunction():

    b = BiDAQ.BiDAQ()
    with b as obj:
        obj.SetLogLevelInfo()
        obj.FlashBoards("/Bessel_CUPID.bin")


if __name__ == '__main__':
    sys.exit(__MainFunction())
