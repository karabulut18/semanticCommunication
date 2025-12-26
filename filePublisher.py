#!/usr/bin/python3

import signal
import time
import zmq
import argparse
import sys
from file_transfer_unit import File_Transfer_Unit
from logger import LOG, LOGE, initialize_logger
from text import textMessage


connection_protocol = 'tcp://'
connection_address = '*:'
connection_string = connection_protocol + connection_address

def signal_handler(sig, frame):
    """Handles system signals (like SIGINT) to exit gracefully."""
    print('Exiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Connection(object):
    """
    Manages the ZeroMQ PUB socket for sending files.
    """
    def __init__(self, port):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDBUF, 8)
        # enable pass tags
        #self.socket.setsockopt(zmq.ZMQ_PASS_TAGS, 1)
        try:
            self.socket.bind(connection_string + str(self.port))
        except Exception as e:
            LOGE(f"Error connecting to port {self.port} {e}")
            exit()
        LOG(f"Connected to port {self.port}")
        self.message_count = 0

    def SetFileTransferUnit(self, fileTransferUnit):
        self.FileTransferUnit = fileTransferUnit

    def send(self, message):
        serialized_message  = message.to_bytes()
        try:
            self.socket.send(serialized_message)
            LOG(f"     Message: {serialized_message}")
            self.message_count += 1
            #log(f"Sent message of size {len(serialized_message)} message count {self.message_count}")
        except Exception as e:
            LOGE(f"Error sending message: {e}")

    def sendStraight(self, message):
        try:
            self.socket.send(message)
        except Exception as e:
            LOGE(f"Error sending message: {e}")

    def __del__(self):
        self.socket.close()
        self.context.term()
    
    def heartbeatLoop(self):
        count = 0
        while True:
            heartbeat = textMessage('Heartbeat ' + str(count))
            LOG(f"Sending heartbeat {count}, size {heartbeat.get_size()}")
            count += 1
            self.send(heartbeat)
            time.sleep(1)


if __name__ == '__main__':
    # Access command-line arguments
    initialize_logger("zmq_pub")
    parser = argparse.ArgumentParser(description="File Publisher (Sender) for Semantic Comm Testbed")
    parser.add_argument('--port', help='Port number to bind to (default: 5555)', type=int, default=5555)
    parser.add_argument('--heartbeatMode', action='store_true', help='Run in heartbeat mode for testing connectivity')
    parser.add_argument('--file_directory', help='Directory containing files to send', default='./sender_side_files')
    args = parser.parse_args()

    port = args.port
    file_directory = args.file_directory

    conn = Connection(port)

    if args.heartbeatMode:
        conn.heartbeatLoop()
    else:
        file_transfer_unit = File_Transfer_Unit(file_directory)
        file_transfer_unit.setConnection(conn)
        conn.SetFileTransferUnit(file_transfer_unit)
        
        LOG("Starting file discovery...")
        file_transfer_unit.findFilesInDirectory()
        time.sleep(1) # Allow subscribers to connect/sync
        
        LOG("Starting transmission...")
        file_transfer_unit.sendAllFiles()

