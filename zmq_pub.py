#!/Users/saka/radioconda/envs/gnuradio/bin/python3

import signal
import time
import zmq
import argparse
import sys
from file_transfer_unit import File_Transfer_Unit
from util.logger import log, loge, initialize_logger
from message.text import textMessage

connection_protocol = 'tcp://'
connection_address = '*:'
connection_string = connection_protocol + connection_address


def signal_handler(sig, frame):
    print('Exiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class connection(object):
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
            loge(f"Error connecting to port {self.port} {e}")
            exit()
        log(f"Connected to port {self.port}")
        self.message_count = 0

    def SetFileTransferUnit(self, fileTransferUnit):
        self.FileTransferUnit = fileTransferUnit

    def send(self, message):
        serialized_message = message.serialize()
        try:
            self.socket.send(serialized_message)
            self.message_count += 1
            #log(f"Sent message of size {len(serialized_message)} message count {self.message_count}")
        except Exception as e:
            loge(f"Error sending message: {e}")

    def sendStraight(self, message):
        try:
            self.socket.send(message)
        except Exception as e:
            loge(f"Error sending message: {e}")

    def __del__(self):
        self.socket.close()
        self.context.term()
    
    def heartbeatLoop(self):
        count = 0
        while True:
            heartbeat = textMessage('Heartbeat ' + str(count))
            log(f"Sending heartbeat {count}, size {heartbeat.get_size()}")
            count += 1
            self.send(heartbeat)
            time.sleep(1)

if __name__ == '__main__':
    # Access command-line arguments
    initialize_logger("zmq_pub")
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port number', type=int)
    parser.add_argument('--heartbeatMode', action='store_false')
    parser.add_argument('--file_directory', help='File directory')
    args = parser.parse_args()
    if args.port:
        port = args.port
    else:
        port = 5555

    if args.file_directory:
        file_directory = args.file_directory
    else:
        file_directory = './sender_side_files'

    connection = connection(port)

    connection.heartbeatLoop()
    '''
        file_transfer_unit = File_Transfer_Unit(file_directory)
    file_transfer_unit.setConnection(connection)
    connection.SetFileTransferUnit(file_transfer_unit)
    file_transfer_unit.findFilesInDirectory()
    time.sleep(5)
    file_transfer_unit.sendAllFiles()
    '''
