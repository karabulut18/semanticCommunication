import enum

# Constants
NAME_BUFFER_SIZE = 256
FILE_BUFFER_SIZE = 1024

# Message Types
class msg_type(enum.Enum):
    MSGTYPE_TEXT = 1
    MSGTYPE_FILE_METADATA = 2
    MSGTYPE_FILE_CONTENT = 3
    MSGTYPE_MAX = 4