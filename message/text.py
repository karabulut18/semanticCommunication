from header import Header, msg_type
from logger import LOG

class textMessage:
    def __init__(self, text):
        self.header = Header(0, msg_type.MSGTYPE_TEXT)
        self.text = text.encode('utf-8')
        self.header.size = self.get_size()

    def get_size(self):
        return self.header.get_size() + self.text.__sizeof__()

    def to_bytes(self):
        return self.header.to_bytes() + self.text
    
    def print_text(self):
        LOG(self.text.decode('utf-8'))

    @classmethod
    def from_bytes(cls, data):
        header = Header.from_bytes(data[:Header.get_size()])
        text = data[Header.get_size():header.size]
        return cls(text.decode('utf-8'))
