import zmq
import json
import time
import netifaces


# Instruct the server to execute a remote function
# Function name is FunctionName, argument list is ArgumentList
def SendFunction(sock, FunctionName, ArgumentList):
    # Create dictionary to be sent via zmq
    D = {'Function': FunctionName, 'ArgumentList': ArgumentList}

    # Debug info
    print('Client - Dictionary:', D)

    # Send message using json
    Message = json.dumps(D)
    sock.send_json(Message)

    # Debug info
    print('Client - Message: ' + Message)

    # Receive result
    Ret = sock.recv_string()
    print('Client - Return value:', Ret)


def main():
    # ZeroMQ Context
    Context = zmq.Context()

    # Define the socket using the "Context"
    # noinspection PyUnresolvedReferences
    Sock = Context.socket(zmq.REQ)
    Sock.connect("tcp://pcelet26.mib.infn.it:2222")

    # Stop DAQ
    SendFunction(Sock, 'StopDaq', [])

    # Send channel config using a list
    # SendFunction(Sock, 'SetChannelConfigList', [[[[0, 1], [0], True, True, 300]]])

    # Send channel config using a dictionary
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

    # Configure FPGA with destination IP and MAC address
    try:
        # These settings are used on the PC near the FPGA
        Interface = 'enp3s0'
        MacStr = netifaces.ifaddresses(Interface)[netifaces.AF_LINK][0]['addr']
        IpAdrStr = netifaces.ifaddresses(Interface)[netifaces.AF_INET][0]['addr']
    except ValueError:
        # These are for Paolo's notebook (although they don't work because data is not delivered over WAN)
        MacStr = 'F8:34:41:D3:FB:85'
        IpAdrStr = '151.21.118.103'

    # Conversions to int
    MacAdrDst = int(MacStr.replace(':', ''), 16)
    IpAdrList = list(map(int, IpAdrStr.split('.')))
    IpAdrDst = int.from_bytes(bytes(IpAdrList), byteorder='big', signed=False)

    # UDP port for data stream
    UDPPort = 2222

    # DAQ frequency
    DAQFreq = 2000

    # Start DAQ
    SendFunction(Sock, 'StartDaq', [MacAdrDst, IpAdrDst, UDPPort, DAQFreq])

    # Wait some time
    time.sleep(2)

    # Stop DAQ
    SendFunction(Sock, 'StopDaq', [])

    return


if __name__ == "__main__":
    main()
