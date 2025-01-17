#!/usr/bin/python3

import signal
import zmq
import argparse
import sys
from file_transfer_unit import File_Transfer_Unit
from logger import LOG, LOGE, initialize_logger
from header import Header, msg_type
from text import textMessage
from fileContent import FileContent
from fileMetaData import FileMetaData


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
            LOGE(f"Error connecting to port {self.port} {e}")
            exit()
        LOG(f"Connected to port {self.port}")
        LOG(f"Subscribed to all message types")
        LOG(f"Listening for messages")
        self.left_over = b''

    def setFileTransferUnit(self, fileTransferUnit):
        self.fileTransferUnit = fileTransferUnit

    def recv(self):
        left_over = b''
        while True:
            data = self.socket.recv()
            #LOG(f"received size {len(data)}- data: {data}") 
            self.ParseMessage(data)
    
    def ParseMessage(self, data):
        header = Header.from_bytes(data[:Header.get_size()])
        message = data[:header.size]
        #log(f"Received message of type {header.msg_type} and size {header.size}")
        if header.msg_type == msg_type.MSGTYPE_TEXT.value:
            self.HandleTextMessage(textMessage.from_bytes(message))
        elif header.msg_type == msg_type.MSGTYPE_FILE_METADATA.value:
            self.fileTransferUnit.HandleFileMetaDataMessage(FileMetaData.from_bytes(message))
        elif header.msg_type == msg_type.MSGTYPE_FILE_CONTENT.value:
            self.fileTransferUnit.HandleFileContentMessage(FileContent.from_bytes(message))
        else:
            pass
            #LOGE(f"Unknown message type {header.msg_type}")
            #LOGE(f"     Message: {message}")
        return data[header.size:]
    def HandleTextMessage(self, message):
        LOG("Received text message")
        message.print_text()

    def recvLoop(self):
        LOG("Starting receiver loop")
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
