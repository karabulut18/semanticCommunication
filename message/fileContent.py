import struct
from header import Header
from util.logger import log, loge
from types import msg_type, FILE_BUFFER_SIZE


class FileContent:
    def __init__(self, file_id, content_buffer, msg_id, file_index):
        self.header                 = Header(0, msg_type.MSGTYPE_FILE_CONTENT)
        self.file_id                = file_id
        self.msg_id                 = msg_id
        self.file_index             = file_index
        self.content_buffer_size    = len(content_buffer)
        self.content_buffer         = content_buffer
        self.header.size            = self.get_size()

    def get_size(self):
        return (Header.get_size() +
                struct.calcsize('!I') +  # file_id
                struct.calcsize('!I') +  # msg_id
                struct.calcsize('!Q') +  # file_index
                struct.calcsize('!Q') +  # content_buffer_size
                self.content_buffer_size)  # content_buffer

    def serialize(self):
        return (self.header.serialize() +
                struct.pack('!I', self.file_id) +
                struct.pack('!I', self.msg_id) +
                struct.pack('!Q', self.file_index) +
                struct.pack('!Q', self.content_buffer_size) +
                self.content_buffer.ljust(self.content_buffer_size, b'\0'))

    @staticmethod
    def deserialize(data):
        offset  = 0
        header  = Header.deserialize(data[offset:offset + Header.get_size()])
        offset  += Header.get_size()
        
        file_id = struct.unpack('!I', data[offset:offset + struct.calcsize('!I')])[0]
        offset  += struct.calcsize('!I')

        msg_id  = struct.unpack('!I', data[offset:offset + struct.calcsize('!I')])[0]
        offset  += struct.calcsize('!I')

        file_index  = struct.unpack('!Q', data[offset:offset + struct.calcsize('!Q')])[0]
        offset      += struct.calcsize('!Q')

        content_buffer_size = struct.unpack('!Q', data[offset:offset + struct.calcsize('!Q')])[0]
        offset              += struct.calcsize('!Q')

        if(content_buffer_size < 0):
            loge(f"Invalid content buffer size {content_buffer_size}")
            return None
        elif(content_buffer_size > FILE_BUFFER_SIZE):
            loge(f"Content buffer size {content_buffer_size} exceeds limit {FILE_BUFFER_SIZE}")
            content_buffer_size = FILE_BUFFER_SIZE

        content_buffer = data[offset:offset + content_buffer_size]

        return FileContent(file_id, content_buffer, msg_id, file_index)
