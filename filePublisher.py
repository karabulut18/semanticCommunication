#!/usr/bin/python3

import signal
import time
import zmq
import argparse
import sys
from file_transfer_unit import File_Transfer_Unit
from logger import LOG, LOGE, initialize_logger
from text import textMessage

from threading import Thread

connection_protocol = 'tcp://'
connection_address = '*:'
connection_string = connection_protocol + connection_address




class connection(object):
    def __init__(self, port):
        self.port       = port
        self.context    = zmq.Context()
        self.socket     = self.context.socket(zmq.PUB)
        #self.socket.setsockopt(zmq.SNDBUF, 128)
        try:
            self.socket.bind(connection_string + str(self.port))
        except Exception as e:
            LOGE(f"Error connecting to port {self.port} {e}")
            exit()
        LOG(f"Connected to port {self.port}")
        self.message_count  = 0
        self.running        = False

    def SetFileTransferUnit(self, fileTransferUnit):
        self.FileTransferUnit = fileTransferUnit

    def send(self, message):
        serialized_message  = message.to_bytes()
        try:
            self.socket.send(serialized_message)
            self.message_count += 1
        except Exception as e:
            LOGE(f"Error sending message: {e}")

    def sendStraight(self, message):
        try:
            self.socket.send(message)
        except Exception as e:
            LOGE(f"Error sending message: {e}")

    def startHeartbeat(self):
        self.heartbeat_thread = Thread(target=self.heartbeatLoop)
        self.heartbeat_thread.start()

    def __del__(self):
        self.running = False
        self.socket.close()
        self.context.term()
    
    def heartbeatLoop(self):
        count = 0
        self.running = True
        while self.running:
            heartbeat = textMessage('Heartbeat ' + str(count))
            LOG(f"Sending heartbeat {count}, size {heartbeat.get_size()}")
            count += 1
            self.send(heartbeat)
            time.sleep(1)
  
    def signal_handler(self, sig, frame):
        print('Exiting program...')
        self.running = False

if __name__ == '__main__':
    # Access command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port number', type=int)
    parser.add_argument('--heartbeatMode', action='store_true', help='Heartbeat mode')
    parser.add_argument('--file_directory', help='File directory')
    parser.add_argument('--debug', help='Debug mode', action='store_true')
    args = parser.parse_args()
    if args.debug:
        initialize_logger("zmq_pub", True)
    else:
        initialize_logger("zmq_pub")

    if args.port:
        port = args.port
    else:
        port = 5555

    if args.file_directory:
        file_directory = args.file_directory
    else:
        file_directory = './sender_side_files'

    connection = connection(port)
    signal.signal(signal.SIGINT, connection.signal_handler)


    if args.heartbeatMode:
        connection.heartbeatLoop()
    else:
        connection.startHeartbeat()
        time.sleep(10)
        file_transfer_unit = File_Transfer_Unit(file_directory)
        file_transfer_unit.setConnection(connection)
        connection.SetFileTransferUnit(file_transfer_unit)
        file_transfer_unit.findFilesInDirectory()
        file_transfer_unit.sendAllFiles()
