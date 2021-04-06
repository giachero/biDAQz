#!/usr/bin/python

from .hwmonitor import HWMonitor
from .portexpander import PortExpander


class BiDAQBackplane:

    # Class constructor
    def __init__(self):

        self.HWMonitor = HWMonitor.HWMonitor()
        self.PortExpander = PortExpander.PortExpander()

        self.Crate = self.PortExpander.GetCrateId()
        self.Half = self.PortExpander.GetCrateHalf()
