#!/Users/saka/radioconda/envs/gnuradio/bin/python3

import signal
import zmq
import argparse
import sys
from file_transfer_unit import File_Transfer_Unit
from util.logger import log, loge, initialize_logger
from message.types import msg_type
from message.header import Header
from message.text import textMessage
from message.fileMetaData import FileMetaData
from message.fileContent import FileContent

connection_protocol = 'tcp://'
connection_address  = 'localhost:'
connection_string   = connection_protocol + connection_address
subscription        = b""

def signal_handler(sig, frame):
    print('Exiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class connection(object):
    def __init__(self, port):
        self.subscription = b''
        self.port       = port
        self.context    = zmq.Context()
        self.socket     = self.context.socket(zmq.SUB)
        # subscribe all predefined message types
        self.socket.setsockopt(zmq.SUBSCRIBE, subscription)

        try:
            #self.socket.connect('tcp://127.0.0.1:' + str(self.port))
            self.socket.connect(connection_string + str(self.port))
        except Exception as e:
            loge(f"Error connecting to port {self.port} {e}")
            exit()
        log(f"Connected to port {self.port}")
        log(f"Subscribed to all message types")
        log(f"Listening for messages")
        self.left_over = b''

    def setFileTransferUnit(self, fileTransferUnit):
        self.fileTransferUnit = fileTransferUnit

    def recv(self):
        data = self.socket.recv()
        #log(f"      Received message of size {len(data)}")
        data = self.left_over + data
        self.left_over = b''
        while len(data) > Header.get_size():
            header = Header.deserialize(data[:Header.get_size()])
            if header.msg_type > msg_type.MSGTYPE_MAX.value or header.msg_type < 1:
                loge(f"Invalid message type {header.msg_type}, message size {len(data)}")
                loge(f"     Message: {data}")
                break
            if header.size > len(data):
                self.left_over = data
                log(f"Left over data size {len(self.left_over)} message size {header.size}")
                break
            message = data[:header.size]
            data = data[header.size:]
            #log(f"Received message of type {header.msg_type} and size {header.size}")
            if header.msg_type == msg_type.MSGTYPE_TEXT.value:
                self.HandleTextMessage(textMessage.deserialize(message))
            elif header.msg_type == msg_type.MSGTYPE_FILE_METADATA.value:
                self.fileTransferUnit.HandleFileMetaDataMessage(FileMetaData.deserialize(message))
            elif header.msg_type == msg_type.MSGTYPE_FILE_CONTENT.value:
                self.fileTransferUnit.HandleFileContentMessage(FileContent.deserialize(message))
            else:
                loge(f"Unknown message type {header.msg_type}")
                loge(f"     Message: {message}")

    def HandleTextMessage(self, message):
        log("Received text message")
        message.print_text()

    def recvLoop(self):
        log("Starting receiver loop")
        self.message_count = 0
        while True:
            self.message_count += 1
            self.recv()
            

    def __del__(self):
        self.socket.close()
        self.context.term()

if __name__ == '__main__':
    initialize_logger("zmq_sink")
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port number', type=int)
    parser.add_argument('--file_directory', help='File directory')
    args = parser.parse_args()
    if args.port:
        port  = args.port
    else:
        port = 5555
    
    if args.file_directory:
        file_directory = args.file_directory
    else:
        file_directory = './receiver_side_files'
    fileTransferUnit = File_Transfer_Unit(file_directory)
    connection = connection(port)
    fileTransferUnit.setConnection(connection)
    connection.setFileTransferUnit(fileTransferUnit)
    connection.recvLoop()
