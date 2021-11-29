#!/usr/bin/python

import BiDAQ
import logging
import sys

def __MainFunction():

    b = BiDAQ.BiDAQ()
    logging.StreamHandler(sys.stdout)
    b.TestBoards()

if __name__ == '__main__':
    sys.exit(__MainFunction())