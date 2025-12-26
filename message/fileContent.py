from header import Header, msg_type, FILE_BUFFER_SIZE
from logger import LOG, LOGE, LOGP, LOGD


class FileContent:
    def __init__(self, file_id, content_buffer, msg_id, file_index):
        self.header                 = Header(0, msg_type.MSGTYPE_FILE_CONTENT)
        self.file_id                = file_id
        self.msg_id                 = msg_id
        self.file_index             = file_index
        self.content_buffer         = content_buffer
        self.content_buffer_size    = len(content_buffer)
        self.header.size            = self.get_size()

    def get_size(self):
        return (Header.get_size() + 4 + 4 + 8 + 8 + self.content_buffer_size)

    def to_bytes(self):
        # Pad the content to a fixed size. Note: connection logic may transmit these padding bytes,
        # but the receiver strips them based on the header size/parsing logic.
        paded_content_buffer = self.content_buffer.ljust(FILE_BUFFER_SIZE, b'\0')
        return (self.header.to_bytes() +
                self.file_id.to_bytes(4, byteorder='big') +
                self.msg_id.to_bytes(4, byteorder='big') +
                self.file_index.to_bytes(8, byteorder='big') +
                self.content_buffer_size.to_bytes(8, byteorder='big') +
                paded_content_buffer)

    def get_content_buffer(self):
        return self.content_buffer[:self.content_buffer_size]

    def debug_print(self):
        LOG(f"File ID: {self.file_id}")
        LOG(f"Message ID: {self.msg_id}")
        LOG(f"File Index: {self.file_index}")
        LOG(f"Content Buffer Size: {self.content_buffer_size}")
        LOGD(f"Content Buffer: {self.content_buffer}")

    @classmethod
    def from_bytes(cls, data):
        try:
            offset = 0
            if len(data) < Header.get_size():
                raise Exception("data is too short to contain the header")

            header = Header.from_bytes(data[offset:offset + Header.get_size()])
            offset += Header.get_size()
            if len(data) < header.size:
                raise Exception("data is too short to contain the message")

            file_id = int.from_bytes(data[offset:offset + 4], byteorder='big')
            offset += 4

            msg_id = int.from_bytes(data[offset:offset + 4], byteorder='big')
            offset += 4

            file_index = int.from_bytes(data[offset:offset + 8], byteorder='big')
            offset += 8

            content_buffer_size = int.from_bytes(data[offset:offset + 8], byteorder='big')
            offset += 8
            if len(data) < offset + content_buffer_size:
                raise Exception("data is too short to contain the content buffer")

            content_buffer = data[offset:offset + content_buffer_size]
            content_buffer.strip(b'\0')
            return cls(file_id, content_buffer, msg_id, file_index)
    
        except Exception as e:
            LOGE(f"Error deserializing content buffer: {e}")
            return None
