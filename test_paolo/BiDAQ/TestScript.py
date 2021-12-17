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
        #obj.CalibrateAllBoards(True)
        Status, BoardRes = obj.CheckGainCalibrationAllBoards(1000, AvgN=1000, GainThrPpm=3, Pause=0.2)


if __name__ == '__main__':
    sys.exit(__MainFunction())
