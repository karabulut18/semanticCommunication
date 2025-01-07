import struct
from enum import Enum

# Constants
NAME_BUFFER_SIZE = 32*2
FILE_BUFFER_SIZE = 32*4
MAX_PACKET_SIZE  = 32*8

# Message Types
class msg_type(Enum):
    MSGTYPE_TEXT = 1
    MSGTYPE_FILE_METADATA = 2
    MSGTYPE_FILE_CONTENT = 3
    MSGTYPE_MAX = 4


class Header:
    def __init__(self, size, msg_type):
        self.size = size
        if isinstance(msg_type, int):
            self.msg_type = msg_type
        else: 
            self.msg_type = msg_type.value

    def serialize(self):
        return struct.pack('!QI', self.size, self.msg_type)  # 12 bytes: 8 for size and 4 for msg_type

    @staticmethod
    def get_size():
        return struct.calcsize('!QI')

    @staticmethod
    def deserialize(data):
        size, msg_type = struct.unpack('!QI', data)
        return Header(size, msg_type)


def PadData(data, size = MAX_PACKET_SIZE):
    return data + b'\0' * (size - len(data)) # Pad with null bytes