#!/usr/bin/python

import BiDAQ
import logging
import sys


def __MainFunction():

    b = BiDAQ.BiDAQ()
    with b as obj:
        obj.SetLogLevelInfo()
        logging.StreamHandler(sys.stdout)
        # obj.TestBoards()
        obj.CalibrateAllBoards(True)


if __name__ == '__main__':
    sys.exit(__MainFunction())
