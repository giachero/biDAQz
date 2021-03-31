# -*- coding: utf-8 -*-
# FROM: https://github.com/lucidm/i2lcd

import smbus


class PCA9535(object):
    INPUT_PORT0 = 0
    INPUT_PORT1 = 1
    OUTPUT_PORT0 = 2
    OUTPUT_PORT1 = 3
    POL_INV0 = 4
    POL_INV1 = 5
    CONF_PORT0 = 6
    CONF_PORT1 = 7

    def __init__(self, bus, address):
        self.bus = smbus.SMBus(bus)
        self.address = address

    def setPort(self, port, value):
        self.bus.write_byte_data(self.address, port, value)

    def getPort(self, port):
        return self.bus.read_byte_data(self.address, port)

    def setPin(self, port, pin, value):
        self.setPort(port, (self.getPort(port) & ~(1 << pin)) | ((value & 1) << pin))

    def getPin(self, port, pin):
        return (self.getPort(port) >> pin) & 1

    def setPortDir(self, port, direction):
        self.setPort(self.CONF_PORT0 + port, direction)

    def getPortDir(self, port):
        return self.getPort(self.CONF_PORT0 + port)

    def setPinDir(self, port, pin, direction):
        self.setPin(self.CONF_PORT0 + port, pin, direction)

    def getPinDir(self, port, pin):
        return self.getPin(self.CONF_PORT0 + port, pin)

    def setPortOutput(self, port, value):
        self.setPort(self.OUTPUT_PORT0 + port, value)

    def getPortOutput(self, port):
        return self.getPort(self.OUTPUT_PORT0 + port)

    def setPinOutput(self, port, pin, value):
        self.setPin(self.OUTPUT_PORT0 + port, pin, value)

    def getPinOutput(self, port, pin):
        return self.getPin(self.OUTPUT_PORT0 + port, pin)

    def getPortInput(self, port):
        return self.getPort(self.INPUT_PORT0 + port)

    def getPinInput(self, port, pin):
        return self.getPin(self.INPUT_PORT0 + port, pin)

    def setPortPolarity(self, port, polarity):
        self.setPort(self.POL_INV0 + port, polarity)

    def getPortPolarity(self, port):
        return self.getPort(self.POL_INV0 + port)

    def setPinPolarity(self, port, pin, polarity):
        self.setPin(self.POL_INV0 + port, pin, polarity)

    def getPinPolarity(self, port, pin):
        return self.getPin(self.POL_INV0 + port, pin)
