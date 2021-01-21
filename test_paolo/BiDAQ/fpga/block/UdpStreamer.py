#!/usr/bin/python

import netifaces

from ..register import FpgaReg


class UdpStreamer:

    # Class constructor
    def __init__(self):

        # Initialize register management class
        self.FpgaReg = FpgaReg.FpgaReg()

    def SetUdpStreamEnable(self, Enable):
        self.FpgaReg.WriteBits("udp_payload_inserter", "EN", Enable)

    def GetUdpStreamEnable(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "EN")

    def GetUdpStreamRunning(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "RUN")

    def GetUdpStreamError(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "ERR")

    def SetUdpStreamDestMac(self, MAC):
        self.FpgaReg.WriteBits("udp_payload_inserter", "DEST_MAC_ADDRESS_LSB", MAC & 0xFFFF)
        self.FpgaReg.WriteBits("udp_payload_inserter", "DEST_MAC_ADDRESS_MSB", (MAC >> 16) & 0xFFFFFFFF)

    def GetUdpStreamDestMac(self):
        MAC_LSB = self.FpgaReg.ReadBits("udp_payload_inserter", "DEST_MAC_ADDRESS_LSB")
        MAC_MSB = self.FpgaReg.ReadBits("udp_payload_inserter", "DEST_MAC_ADDRESS_MSB")
        return MAC_LSB | (MAC_MSB << 16)

    def SetUdpStreamSourMac(self, MAC):
        self.FpgaReg.WriteBits("udp_payload_inserter", "SOUR_MAC_ADDRESS_LSB", MAC & 0xFFFF)
        self.FpgaReg.WriteBits("udp_payload_inserter", "SOUR_MAC_ADDRESS_MSB", (MAC >> 16) & 0xFFFFFFFF)

    def GetUdpStreamSourMac(self):
        MAC_LSB = self.FpgaReg.ReadBits("udp_payload_inserter", "SOUR_MAC_ADDRESS_LSB")
        MAC_MSB = self.FpgaReg.ReadBits("udp_payload_inserter", "SOUR_MAC_ADDRESS_MSB")
        return MAC_LSB | (MAC_MSB << 16)

    def SetUdpStreamDestIp(self, IP):
        self.FpgaReg.WriteBits("udp_payload_inserter", "DEST_IP_ADDRESS", IP)

    def GetUdpStreamDestIp(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "DEST_IP_ADDRESS")

    def SetUdpStreamSourIp(self, IP):
        self.FpgaReg.WriteBits("udp_payload_inserter", "SOUR_IP_ADDRESS", IP)

    def GetUdpStreamSourIp(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "SOUR_IP_ADDRESS")

    def AutoSetUdpStreamSourAddr(self):

        # Get own IP and MAC addresses from eth0 interface
        Interface = 'eth0'

        # Get MAC address
        MacStr = netifaces.ifaddresses(Interface)[netifaces.AF_LINK][0]['addr']
        # Convert to integer
        Mac = int(MacStr.replace(':', ''), 16)
        # Set own MAC
        self.SetUdpStreamSourMac(Mac)

        # Get IP address
        # noinspection PyBroadException
        try:
            ipAdrStr = netifaces.ifaddresses(Interface)[netifaces.AF_INET][0]['addr']
        except:
            ipAdrStr = '127.0.0.1'
        # Convert to list
        ipAdrList = list(map(int, ipAdrStr.split('.')))
        # Convert to integer
        ipAdr = int.from_bytes(bytes(ipAdrList), byteorder='big', signed=False)
        # Set own IP address
        self.SetUdpStreamSourIp(ipAdr)

    def SetUdpStreamDestPort(self, Port):
        self.FpgaReg.WriteBits("udp_payload_inserter", "DEST_UDP_PORT", Port)

    def GetUdpStreamDestPort(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "DEST_UDP_PORT")

    def SetUdpStreamSourPort(self, Port):
        self.FpgaReg.WriteBits("udp_payload_inserter", "SOUR_UDP_PORT", Port)

    def GetUdpStreamSourPort(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "SOUR_UDP_PORT")

    def GetUdpStreamPacketCount(self):
        return self.FpgaReg.ReadBits("udp_payload_inserter", "PACKET_COUNT")

    def GetMonitorRegisters(self):
        RetDict = dict()

        RetDict["UdpStreamer"] = dict()
        RetDict["UdpStreamer"]["PacketsSent"] = self.GetUdpStreamPacketCount()

        return RetDict