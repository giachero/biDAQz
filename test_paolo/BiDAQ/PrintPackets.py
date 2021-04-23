import BiDAQ


def main():

    b = BiDAQ.BiDAQ()

    PktsDataPacketizer = b.FPGA.DataPacketizer.GetPacketCount(8)
    for i in b.BoardList:
        PktsDataPacketizer += b.FPGA.DataPacketizer.GetPacketCount(i)

    PktsUdpStreamer = b.FPGA.UdpStreamer.GetUdpStreamPacketCount()

    with open('/sys/class/net/eth0/statistics/tx_packets') as TxPackets:
        PktsEth0 = int(TxPackets.read())

    c = b.FPGA.TxMac.GetMonitorRegisters()
    PktsTxMacUnicast = c['TxMac']['UnicastPackets']
    PktsTxMacSent = c['TxMac']['PacketsSent']

    print('Data Packetizer: ', PktsDataPacketizer)
    print('Udp Streamer:    ', PktsUdpStreamer)
    # print('TxMacUnicast - Eth0', PktsTxMacUnicast - PktsEth0)
    print('TxMacSent - Eth0:', PktsTxMacSent - PktsEth0)


if __name__ == "__main__":
    main()
