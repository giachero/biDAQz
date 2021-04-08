#!/usr/bin/python

from . import DevMem


############################################################
# Class to access the HPS ir FPGA registers                #
############################################################
class Reg:

    # Class constructor
    def __init__(self, BaseAdr, MemLen, RegDict):

        # Initialize DevMem class
        self.RegMem = DevMem.DevMem(BaseAdr, MemLen)

        # Create dictionary
        self.RegDict = RegDict

    # Get register from the dictionary
    # Returns register address as first element, then high bit range and low bit range as second and third elements,
    # if a bit name was specified. If BitName is empty, only the address is returned
    # If there is an error or nothing is found, -1 is returned
    def GetRegister(self, RegName, BitName):

        # Find register in the first level of RegDict
        if RegName in self.RegDict:

            # Extract register
            reg = self.RegDict[RegName]

            # If the register has other sub-registers
            if isinstance(reg, dict):

                # Cycle through the sub-registers
                for key in reg.keys():

                    # Extract bit names from the sub-register
                    SubRegBitNames = reg[key][1]

                    # If the bit name is in the current sub-register
                    if BitName in SubRegBitNames.keys():
                        # Extract the sub-register address
                        RegAdr = reg[key][0]

                        # Extract bit ranges for the selected bit name
                        BitRange = SubRegBitNames[BitName]
                        BitRangeH = BitRange[1]
                        BitRangeL = BitRange[0]

                        # Return address and ranges
                        return RegAdr, BitRangeH, BitRangeL

            # If the register doesn't have any sub-register
            else:

                # If the bit name is in the current register
                if BitName in reg[1]:

                    # Extract the register address
                    RegAdr = reg[0]

                    # Extract bit ranges for the selected bit name
                    BitRange = reg[1][BitName]
                    BitRangeH = BitRange[1]
                    BitRangeL = BitRange[0]

                    # Return address and ranges
                    return RegAdr, BitRangeH, BitRangeL

                # If no bit name is specified, the whole register is required
                elif not BitName:
                    RegAdr = reg[0]
                    return RegAdr

                # Otherwise nothing was found or there is something wrong
                else:
                    return -1

        # If the register was not found in the first level of the dictionary hierarchy, it could be in the second
        else:

            # Cycle through the first level registers
            for key in self.RegDict.keys():

                # Extract sub-register
                SubRegs = self.RegDict[key]

                # If sub-register is a dictionary itself
                if isinstance(SubRegs, dict):

                    # Check if the required reg is withing this dictionary
                    if RegName in SubRegs.keys():
                        # Return the address of this register
                        return SubRegs[RegName][0]

        # Otherwise nothing was found anywhere...
        return -1

    # Read the whole register
    def ReadRegister(self, RegName):

        # Get register address
        RegAdr = self.GetRegister(RegName, None)
        if RegAdr == -1:
            # Error
            return RegAdr
        else:
            # Read register data
            Value = self.RegMem.read(RegAdr, 1)
            return Value[0]

    # Write the whole register
    def WriteRegister(self, RegName, Value):

        # Get register address
        RegAdr = self.GetRegister(RegName, None)
        if RegAdr == -1:
            # Error
            return RegAdr
        else:
            # Write register
            self.RegMem.write(RegAdr, [Value])
            return 0

    # Read a specific bit (or group of bits) BitName, from a register RegName
    def ReadBits(self, RegName, BitName):

        # Get register address and bit range
        Ret = self.GetRegister(RegName, BitName)
        if Ret == -1:
            # Error
            return Ret
        else:
            # Extract address and ranges
            RegAdr, BitRangeH, BitRangeL = Ret
            # Read whole address
            Value = self.RegMem.read(RegAdr, 1)
            # Mask away undesired bits
            Value = Value[0] & ((2 ** (BitRangeH - BitRangeL + 1) - 1) << BitRangeL)
            # Return requested bits
            return Value >> BitRangeL

    # Write a specific bit (or group of bits) BitName, from a register RegName
    def WriteBits(self, RegName, BitName, Data):

        # Get register address and bit range
        Ret = self.GetRegister(RegName, BitName)
        if Ret == -1:
            # Error
            return Ret
        else:
            # Extract address and ranges
            RegAdr, BitRangeH, BitRangeL = Ret
            # Read whole address
            Value = self.RegMem.read(RegAdr, 1)
            # Create masks with selected bits
            Mask = (2 ** (BitRangeH - BitRangeL + 1) - 1)
            # Clear all the bits in the selected range
            Value = Value[0] & ~(Mask << BitRangeL)
            # Update register with new data
            Value = Value | ((Data & Mask) << BitRangeL)
            # Write to memory
            self.RegMem.write(RegAdr, [Value])
            return 0

    # Dump FPGA registers
    def DumpRegisterList(self, RegList):

        # Initialize dictionary
        DumpDict = {}
        # Cycle through the list
        for RegName in RegList:
            # Get register data
            Value = self.ReadRegister(RegName)
            if Value < 0:
                # Error
                raise Exception("Register not found - RegName: {}".format(RegName))
            else:
                # Fill the dictionary with register data
                DumpDict[RegName] = Value

        return DumpDict

    # Reload a register dump dictionary
    def LoadRegisterList(self, DumpDict):

        # Cycle through the list
        for RegName in DumpDict.keys():
            # Write back the register with data from the dictionary
            if self.WriteRegister(RegName, DumpDict[RegName]) < 0:
                # Error
                raise Exception("Register not found - RegName: {}".format(RegName))

        return 0
