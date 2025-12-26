from header import Header, msg_type, NAME_BUFFER_SIZE
from logger import LOGE


class FileMetaData:
    def __init__(self, file_name, file_size, file_id):
        self.header         = Header(0, msg_type.MSGTYPE_FILE_METADATA)
        self.file_size      = file_size
        self.file_id        = file_id
        self.file_name      = file_name.encode('utf-8')
        self.file_name_size = len(self.file_name)
        self.header.size    = self.get_size()

    def get_file_name(self):
        return self.file_name.decode('utf-8')

    def get_size(self):
        return Header.get_size() + 20 + self.file_name_size

    def to_bytes(self):
        return (self.header.to_bytes() +
                self.file_size.to_bytes(8, byteorder='big') +
                self.file_id.to_bytes(4, byteorder='big') +
                self.file_name_size.to_bytes(8, byteorder='big') +
                self.file_name)

    @classmethod
    def from_bytes(cls, data):
        offset = 0
        header = Header.from_bytes(data[offset:offset + Header.get_size()])
        offset += Header.get_size()

        file_size = int.from_bytes(data[offset:offset + 8], byteorder='big')
        offset += 8

        file_id = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4

        file_name_size = int.from_bytes(data[offset:offset + 8], byteorder='big')
        offset += 8

        try:
            file_name = data[offset:offset + file_name_size]
        except Exception as e:
            LOGE(f"Error deserializing file name: {e}")
            return None

        return cls(file_name.decode('utf-8'), file_size, file_id)