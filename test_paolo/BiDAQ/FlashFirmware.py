#!/usr/bin/python

import BiDAQ
import sys


def __MainFunction():

    b = BiDAQ.BiDAQ(Verbose=True)
    with b as obj:
        obj.FlashBoards("/Bessel_CUPID.bin")


if __name__ == '__main__':
    sys.exit(__MainFunction())
