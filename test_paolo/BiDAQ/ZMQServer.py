#!/usr/bin/python

import zmq
import netifaces
import json
import BiDAQ
import logging
import sys

log = logging.getLogger("ZMQServer")


def wrapper(func, args):
    return func(*args)


def main():
    LogLevel = logging.INFO

    logging.basicConfig(stream=sys.stderr, level=LogLevel)

    # ZeroMQ Context
    Context = zmq.Context()

    # Define the socket using the "Context"
    # noinspection PyUnresolvedReferences
    Sock = Context.socket(zmq.REP)

    # Get own IP address
    Interface = 'eth0'
    IpAdrStr = netifaces.ifaddresses(Interface)[netifaces.AF_INET][0]['addr']
    Port = 2222

    # Bind the socket to own IP and port
    Sock.bind('tcp://' + IpAdrStr + ':' + str(Port))

    # Init crate and board numbers
    # For future: read these values from GPIOs and/or FPGA
    Crate = 0
    Boards = [0, 1]
    Daq = BiDAQ.BiDAQ(Crate, Boards)

    # Parser server
    while True:
        # Receive JSON string
        Message = Sock.recv_json()
        # Parse JSON string to dictionary
        InputDict = json.loads(Message)
        # Default return value
        Ret = 'ERR'
        # Check input dictionary fields
        if 'Function' in InputDict and 'ArgumentList' in InputDict:
            log.info("Got function ({}) with arguments ({})".format(InputDict['Function'],
                                                                    InputDict['ArgumentList']))
            try:
                # Get function from the class
                Function = getattr(Daq, InputDict['Function'])
            except AttributeError:
                # If not found, return error string
                Ret = 'ERR'
            else:
                # Execute function with the received argument list
                Result = wrapper(Function, InputDict['ArgumentList'])
                # If everything is fine, return ok string
                if Result == 0:
                    Ret = 'OK'

        # Send return string back to the client
        Sock.send_string(Ret)


if __name__ == "__main__":
    main()
