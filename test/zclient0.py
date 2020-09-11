#!/usr/bin/env python

import zmq
import sys


def main():

    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using the "Context"
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://127.0.0.1:5678")

    
    for i in range(1,11):
        # Send a "message" using the socket
        sock.send('Hello {i:02d}'.format(i=i))

        #sock.send(bytes(, encoding='utf-8'))
        #sock.send(bytes('Hello', encoding='utf-8'))
        print ('Client: '+sock.recv().decode("utf-8"))
    
    return
    
if __name__ == "__main__":
    main()
    
    
