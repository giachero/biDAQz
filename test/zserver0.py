#!/usr/bin/env python

import zmq

def main():

    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using the "Context"
    sock = context.socket(zmq.REP)
    sock.bind("tcp://127.0.0.1:5678")

    # Run a simple "Echo" server
    while True:
        message = sock.recv()
        message = message.decode("utf-8")
        
        sock.send(bytes('Echo: '+message+ ' received' , encoding='utf-8'))
        print ('Server: '+message+ ' received')

    return


if __name__ == "__main__":
    main()
