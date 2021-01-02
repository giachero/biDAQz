import zmq
import json
import time
import netifaces


def SendFunction(sock, FunctionName, ArgumentList):
    D = {'Function': FunctionName, 'ArgumentList': ArgumentList}

    print('Client - Dictionary:', D)

    Message = json.dumps(D)
    sock.send_json(Message)

    print('Client - Message: ' + Message)

    Ret = sock.recv_string()
    print('Client - Return value:', Ret)


def main():
    # ZeroMQ Context
    Context = zmq.Context()

    # Define the socket using the "Context"
    # noinspection PyUnresolvedReferences
    Sock = Context.socket(zmq.REQ)
    Sock.connect("tcp://192.168.1.2:5678")

    SendFunction(Sock, 'StopDaq', [])

    # SendFunction(Sock, 'SetChannelConfigList', [[[[0, 1], [0], True, True, 300]]])

    SettingDict = {'Board0_half0': {'Board': [0, 1],
                                    'Channel': [1, 2, 3, 4, 5, 6],
                                    'Ground': True,
                                    'Enable': True,
                                    'Freq': 24},
                   'Board0_half1': {'Board': [0, 1],
                                    'Channel': [7, 8, 9, 10, 11, 12],
                                    'Ground': True,
                                    'Enable': True,
                                    'Freq': 2500},
                   }
    SendFunction(Sock, 'SetChannelConfigDict', [SettingDict])

    Interface = 'enp3s0'
    MacStr = netifaces.ifaddresses(Interface)[netifaces.AF_LINK][0]['addr']
    MacAdrDst = int(MacStr.replace(':', ''), 16)
    IpAdrStr = netifaces.ifaddresses(Interface)[netifaces.AF_INET][0]['addr']
    IpAdrList = list(map(int, IpAdrStr.split('.')))
    IpAdrDst = int.from_bytes(bytes(IpAdrList), byteorder='big', signed=False)
    UDPPort = 5060
    DAQFreq = 2000
    SendFunction(Sock, 'StartDaq', [MacAdrDst, IpAdrDst, UDPPort, DAQFreq])

    time.sleep(2)

    SendFunction(Sock, 'StopDaq', [])

    return


if __name__ == "__main__":
    main()
