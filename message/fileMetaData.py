import struct
from header import Header, msg_type, NAME_BUFFER_SIZE
from logger import LOGE


class FileMetaData:
    def __init__(self, file_name, file_size, file_id):
        self.header         = Header(0, msg_type.MSGTYPE_FILE_METADATA)
        self.file_size      = file_size
        self.file_id        = file_id
        self.file_name_size = len(file_name)
        self.file_name      = file_name.encode('utf-8')
        self.header.size    = self.get_size()

    def get_size(self):
        return Header.get_size() + struct.calcsize('!Q') + struct.calcsize('!I') + struct.calcsize('!Q') + self.file_name_size

    def serialize(self):
        # ensure put a terminating null byte at the end of the file name
        return (self.header.serialize() + 
                struct.pack('!QI', self.file_size, self.file_id) + 
                struct.pack('!Q', self.file_name_size) + 
                self.file_name.ljust(self.file_name_size, b'\0'))

    @staticmethod
    def deserialize(data):
        header_size         = Header.get_size()
        header              = Header.deserialize(data[:header_size])
        offset              = header_size

        file_size, file_id  = struct.unpack('!QI', data[offset:offset + struct.calcsize('!Q') + struct.calcsize('!I')])
        offset              += struct.calcsize('!QI')

        file_name_size      = struct.unpack('!Q', data[offset:offset + struct.calcsize('!Q')])[0]
        offset              += struct.calcsize('!Q')

        if(file_name_size < 0):
            LOGE(f"Invalid file name size {file_name_size}")
            return None
        elif(file_name_size > NAME_BUFFER_SIZE):
            LOGE(f"File name size {file_name_size} exceeds limit {NAME_BUFFER_SIZE}")
            file_name_size = NAME_BUFFER_SIZE

        file_name           = data[offset:offset + file_name_size].decode('utf-8')
        return FileMetaData(file_name, file_size, file_id)
