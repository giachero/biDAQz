#!/usr/bin/python

import netifaces
import subprocess

from ..register import FpgaReg


def GetMacFromIp(Ip, PingFlag=False):
    # Default return value
    Mac = None
    # Perform ping, only if requested
    if PingFlag:
        # Ping the requested IP
        Ping = subprocess.Popen(['ping', '-c 1 -W 1', str(Ip)], stdout=subprocess.PIPE)
        while True:
            # Poll return code
            ReturnCode = Ping.poll()
            if ReturnCode is not None:
                # If successful, break polling loop
                break
    # Read ARP table
    Arp = subprocess.Popen('ipneigh', stdout=subprocess.PIPE)
    while True:
        # Poll return code
        ReturnCode = Arp.poll()
        if ReturnCode is not None:
            # Get command output
            Output, Err = Arp.communicate()
            # Decode it to string
            OutputStr = Output.decode('utf-8')
            # Parse rows
            for Row in OutputStr.splitlines():
                # Split row fields
                RowSplit = Row.split()
                # Convert first field to IP address (decimal)
                IpFromStr = int.from_bytes(list(map(int, RowSplit[0].split('.'))), 'big')
                # If IP address matches the one requested, extract the MAC address (decimal)
                if Ip == IpFromStr:
                    print(RowSplit[-1])
                    if RowSplit[-1] != "FAILED":
                        Mac = int(RowSplit[4].replace(':', ''), 16)
                        break
            # After parsing all the rows, break polling
            break
    # Return MAC address
    return Mac


def GetMacGateway():
    # Get IP address of the gateway
    IpGateway = int.from_bytes(list(map(int, netifaces.gateways()['default'][netifaces.AF_INET][0].split('.'))), 'big')
    # Return its MAC address
    return GetMacFromIp(IpGateway)


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

    def AutoSetUdpStreamDestMac(self):
        # Get destination IP address set previously
        IP = self.GetUdpStreamDestIp()
        # Get MAC from this address, without ping (using current ARP table)
        MAC = GetMacFromIp(IP, False)
        # If no MAC is found, repeat operation with ping (to update ARP table)
        if MAC is None:
            MAC = GetMacFromIp(IP, True)
        # If no MAC is found, then the IP must be outside the local network. Get the gateway MAC
        if MAC is None:
            MAC = GetMacGateway()
        # Set the MAC
        self.SetUdpStreamDestMac(MAC)
        return 0

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
