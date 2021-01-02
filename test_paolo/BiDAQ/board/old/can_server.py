#!/usr/bin/python

from multiprocessing import Process, Pipe, Queue
import os
import sys

import can
import devmem


TX_PIPE = 'can_server_tx_pipe'
RX_PIPE = 'can_server_rx_pipe'

def printDebug (something):
	debugFlag = True
	if debugFlag:
		print(something)



def main():

	try:
    		os.mkfifo(TX_PIPE)
	except OSError: 
    		raise

	try:
    		os.mkfifo(RX_PIPE)
	except OSError: 
    		raise

	with open(NAMED_PIPE) as fifo:
		while True:
			data = fifo.read()
			if len(data) == 0:
 				break
			print('[x] Data: {}'.format(data))


	bus = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)
	reader = can.BufferedReader()
	notifier = can.Notifier(bus, [reader])


	listener = can.Listener()
        listener.on_message_received = callback

cmd = {\
'NOP':(0,[0]),\
'FW_VER_READ':(81+128,[0]),\
'FILTER_ENABLE_WRITE':(1,[1]),\
'FILTER_ENABLE_READ':(1+128,[0]),\
'FREQUENCY_WRITE':(2,[1,2]),\
'FREQUENCY_READ':(2+128,[0]),\
'INPUT_GROUND_WRITE':(3,[1]),\
'INPUT_GROUND_READ':(3+128,[0]),\
'FREQUENCY_AND_ENABLE':(4,[0]),\
'ADC_FREQ_WRITE':(33,[1,2,3,4]),\
'ADC_FREQ_READ':(33+128,[0]),\
'ADC_CONTINUOUS':(61,[1]),\
'ADC_STOP':(62,[0]),\
'MODE_WRITE':(48,[1]),\
'MODE_READ':(48+128,[0]),\
}

cmdList = cmd[sys.argv[1]]
cmdSel = cmdList[0]
boardNum = int(sys.argv[2])
channelNum = int(sys.argv[3])
outData  = int(sys.argv[4])
outDataBytes = outData.to_bytes(4, 'little')

outDataFinal = [cmdSel, 0, 0, 0, 0, 0]

if all(x > 0 for x in cmdList[1]):
   for i in cmdList[1]:
      outDataFinal[i] = outDataBytes[len(cmdList[1])-i]

if debugFlag:
   print(outDataFinal)

canId = int("0x00410000", 16) + boardNum*16 + channelNum

outMsg = can.Message(data = outDataFinal)
outMsg.is_extended_id = True
outMsg.arbitration_id = canId

bus.send(outMsg)
inMsg = reader.get_message(2)

if debugFlag:
    print(inMsg)

inCmd = inMsg.data[0]
inData = int.from_bytes(inMsg.data[1:-1], byteorder='big', signed=False)
inStatus = inMsg.data[-1]

print(inCmd, inData, inStatus)

#baseAdr = int("0xC0000000",16)
#udpPayloadInserterAdr = int("0x20000",16)
#udpPayloadInserter = devmem.DevMem(baseAdr + udpPayloadInserterAdr, 1)
#booh = udpPayloadInserter.read(0,1)
#
#print(booh)

sys.exit(inStatus)

if __name__ == "__main__":
	main()
