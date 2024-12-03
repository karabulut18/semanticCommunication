import struct


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