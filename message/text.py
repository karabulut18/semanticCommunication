from header import Header
from types import msg_type
from util.logger import log


class textMessage:
    def __init__(self, text):
        self.header = Header(0, msg_type.MSGTYPE_TEXT)
        self.text = text
        self.header.size = self.get_size()

    def get_size(self):
        return self.header.get_size() + len(self.text)

    def serialize(self):
        return self.header.serialize() + self.text.encode('utf-8')
    
    def print_text(self):
        log(self.text)

    @staticmethod
    def deserialize(data):
        header = Header.deserialize(data[:Header.get_size()])
        text = data[Header.get_size():]
        # if text is already decoded, then return textMessage(text)
        if isinstance(text, str):
            return textMessage(text)
        return textMessage(text.decode('utf-8'))
