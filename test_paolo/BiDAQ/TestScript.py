#!/usr/bin/python

import BiDAQ
import logging
import sys

def __MainFunction():

    b = BiDAQ.BiDAQ()
    b.SetLogLevelInfo()
    logging.StreamHandler(sys.stdout)
    # b.TestBoards()
    b.CalibrateAllBoards(True)

if __name__ == '__main__':
    sys.exit(__MainFunction())