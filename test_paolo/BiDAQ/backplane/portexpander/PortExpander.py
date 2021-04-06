from . import PCA9535


class PortExpander:

    # Class constructor
    def __init__(self):

        # Init chips
        self.Chip = list()
        self.Chip.append(PCA9535.PCA9535(0, 0x20))
        self.Chip.append(PCA9535.PCA9535(0, 0x21))

        # Set crate address pins as inputs
        for Pin in range(5):
            self.Chip[0].setPinDir(0, Pin, 1)

        # Set GPIO port mappings: 0 and 1 to chip 0, 2 and 3 to chip 1
        self.ChipMapping = (0, 0, 1, 1)
        self.PortMapping = (0, 1, 0, 1)

        # Set forbidden pins (those used by the crate address)
        self.ChipForbidden = (0, 0, 0, 0, 0)
        self.PortForbidden = (0, 0, 0, 0, 0)
        self.PinForbidden = (0, 1, 2, 3, 4)

    def GetCrateId(self):
        return (self.Chip[0].getPortInput(0) >> 1) & 0xf

    def GetCrateHalf(self):
        return (self.Chip[0].getPortInput(0) & 1)

    def CheckAllowed(self, Port, Pin):
        if self.ChipMapping[Port] in self.ChipForbidden and self.PortMapping[Port] in self.PortForbidden \
                and Pin in self.PinForbidden:
            return False
        else:
            return True

    def SetPinDir(self, Port, Pin, Dir):
        if self.CheckAllowed(Port, Pin):
            self.Chip[self.ChipMapping[Port]].setPinDir(self.PortMapping[Port], Pin, Dir)

    # TODO: Expand functions
