#!/usr/bin/python

import can


debugFlag = True

bus1 = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)
reader1 = can.BufferedReader()
notifier1 = can.Notifier(bus1, [reader1])

bus2 = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)
reader2 = can.BufferedReader()
notifier2 = can.Notifier(bus2, [reader2])

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

cmdList = cmd['FW_VER_READ']
cmdSel = cmdList[0]
boardNum = 0
channelNum = 0
outData  = [0, 0, 0, 0]
outDataBytes = [0, 0, 0, 0]

outDataFinal = [cmdSel, 0, 0, 0, 0, 0]

if all(x > 0 for x in cmdList[1]):
   for i in cmdList[1]:
      outDataFinal[i] = outDataBytes[len(cmdList[1])-i]

if debugFlag:
   print(outDataFinal)

canId1 = int("0x00410000", 16) + boardNum*16 + channelNum
canId2 = int("0x00410000", 16) + (boardNum+1)*16 + channelNum

bus1.set_filters([{"can_id": canId1, "can_mask": 0x1FFFFFF0, "extended": True}])
bus2.set_filters([{"can_id": canId2, "can_mask": 0x1FFFFFF0, "extended": True}])

outMsg1 = can.Message(data = outDataFinal)
outMsg1.is_extended_id = True
outMsg1.arbitration_id = canId1

outMsg2 = can.Message(data = outDataFinal)
outMsg2.is_extended_id = True
outMsg2.arbitration_id = canId2

bus1.send(outMsg1)
inMsg1 = reader1.get_message()
inMsg2 = reader2.get_message()

if debugFlag:
	print('inMsg1', inMsg1)
	print('inMsg2', inMsg2)

inMsg1 = reader1.get_message()
inMsg2 = reader2.get_message()

if debugFlag:
	print('inMsg1', inMsg1)
	print('inMsg2', inMsg2)

bus2.send(outMsg2)
inMsg1 = reader1.get_message()
inMsg2 = reader2.get_message()

if debugFlag:
	print('inMsg1', inMsg1)
	print('inMsg2', inMsg2)

inMsg1 = reader1.get_message()
inMsg2 = reader2.get_message()

if debugFlag:
	print('inMsg1', inMsg1)
	print('inMsg2', inMsg2)

inCmd = inMsg1.data[0]
inData = int.from_bytes(inMsg1.data[1:-1], byteorder='big', signed=False)
inStatus = inMsg1.data[-1]

print(inCmd, inData, inStatus)

inCmd = inMsg2.data[0]
inData = int.from_bytes(inMsg2.data[1:-1], byteorder='big', signed=False)
inStatus = inMsg2.data[-1]

print(inCmd, inData, inStatus)

