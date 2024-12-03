import util.file_utl as file_utl
from message.fileContent import FileContent
from message.types import FILE_BUFFER_SIZE
from util.logger import log, loge

class File(object):
    def __init__(self, file_name, file_path, id):
        self.file_name  = file_name
        self.file_path  = file_path
        self.id         = id
        self.file_index = 0

    def createFile(self):
        return file_utl.create_file(self.file_path)
    
    def setFileSize(self, size):
        self.size = size

    def getPartialFileContent(self):
        file_read_size = 0
        if FILE_BUFFER_SIZE > self.size - self.file_index:
            file_read_size = self.size - self.file_index
        else:
            file_read_size = FILE_BUFFER_SIZE

        file_content        = file_utl.read_binary_file_with_start_end_index(self.file_path, self.file_index, self.file_index + file_read_size)
        file_index          = self.file_index
        self.file_index     += file_read_size
        return file_content, file_index

    def writeContentToFile(self, content, file_index):
        #log(f"Writing content to file {self.file_name} with start index {self.file_index}")
        #log(f"Content size {len(content)}")
        if(file_index > self.size):
            loge(f"File {self.file_name} index out of bounds")
            return
        file_utl.write_to_file_with_start_index(self.file_path, content, file_index)
        self.file_index += len(content)
        if self.file_index >= self.size:
            log(f"File {self.file_name} transfer complete")
            self.file_index = 0
