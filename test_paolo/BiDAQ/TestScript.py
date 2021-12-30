#!/usr/bin/python

import BiDAQ
import logging
import sys


def __MainFunction():

    # FilterFreq = 100

    b = BiDAQ.BiDAQ()

    # BOARD SELF TEST
    # with b as obj:
    #     obj.SetLogLevelInfo()
    #     logging.StreamHandler(sys.stdout)
    #     obj.TestBoards()

    # BOARD CALIBRATION
    # with b as obj:
    #     obj.SetLogLevelInfo()
    #     logging.StreamHandler(sys.stdout)
    #     for Brd in obj.BoardList:
    #         obj.Board[Brd].WriteFilterSettingsWithADCCalibration(0, FilterFreq, 1, 1)
    #     obj.CalibrateAllBoards(True, FilterFreq=FilterFreq, DaqFreq=FilterFreq*10)
    #     Status, BoardRes = obj.CheckGainCalibrationAllBoards(DaqFreq=FilterFreq*10, AvgN=100, GainThrPpm=10,
    #                                                          Pause=0.2)

    # BOARD TEST CALIBRATION AT DIFFERENT SETTINGS
    with b as obj:
        BoardRes = list()
        FreqRes = list()
        for FilterFreq in [25, 50, 100, 150, 230, 350, 500, 750, 1125, 1700, 2200]:
            # obj.SetLogLevelInfo()
            logging.StreamHandler(sys.stdout)
            print("Filter frequency: {} Hz".format(FilterFreq))
            for Brd in obj.BoardList:
                obj.Board[Brd].WriteFilterSettingsWithADCCalibration(0, FilterFreq, 1, 1)
                CmdRet = obj.Board[Brd].WriteFilterFrequency(0, FilterFreq)
            FreqRes = FreqRes + [CmdRet.Value]
            # obj.CalibrateAllBoards(True, FilterFreq=FilterFreq, DaqFreq=FilterFreq*10)
            # Status, BoardResTmp = obj.CheckGainCalibration(Board=0, DaqFreq=FilterFreq*10, AvgN=100, GainThrPpm=0,
            #                                                        Pause=0.2)
            Status, BoardResTmp = obj.CheckGainCalibration(Board=0, DaqFreq=FilterFreq*10, AvgN=200, GainThrPpm=0,
                                                           Pause=0.2)
            BoardRes = BoardRes + [BoardResTmp]
        print(BoardRes)
        print(FreqRes)


if __name__ == '__main__':
    sys.exit(__MainFunction())
