from enum import Enum

# Constants
NAME_BUFFER_SIZE = 128
FILE_BUFFER_SIZE = 1024

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

    def to_bytes(self):
        # 12 bytes: 8 for size and 4 for msg_type
        return  self.size.to_bytes(8, byteorder='big') + self.msg_type.to_bytes(4, byteorder='big')

    @staticmethod
    def get_size():
        return 12

    @classmethod
    def from_bytes(cls, data):
        size = int.from_bytes(data[:8], byteorder='big')
        msg_type = int.from_bytes(data[8:12], byteorder='big')
        return cls(size, msg_type)
