import file_utl as file_utl
from file import File
from time import sleep
from logger import LOG, LOGE
from fileMetaData import FileMetaData
from fileContent import FileContent

class File_Transfer_Unit(object):
    """
    Manages the high-level logic for file discovery, chunking, and reconstruction.
    Acts as the bridge between the file system and the connection layer.
    """
    def __init__(self, file_directory):
        file_dir = file_utl.convert_relative_path_to_absolute_path(file_directory)
        self.file_directory = file_dir
        self.files = {}
        self.fileTransferIndex = 0
        self.msgcount = 0

    def setConnection(self, connection):
        self.connection = connection

    def deleteFiles(self):
        for file_id in self.files:
            file_utl.remove_file(self.files[file_id].file_path)

    def findFilesInDirectory(self):
        files = file_utl.get_files_in_dir(self.file_directory)
        for file in files:
            file_path = self.file_directory + '/' + file
            file_path = file_utl.expand_path(file_path)
            fileObject = File(file, file_path, self.fileTransferIndex)
            fileSize = file_utl.get_file_size(file_path)
            fileObject.setFileSize(fileSize)
            LOG(f"File {file} found with size {fileSize}")
            self.files[self.fileTransferIndex] = fileObject
            self.fileTransferIndex += 1

    def sendMetaData(self, file_id):
        file = self.files[file_id]
        fileMetaData = FileMetaData(file.file_name, file.size, file.id)
        self.connection.send(fileMetaData)
        LOG(f"File meta data sent for file id {file.id}, file name {file.file_name}, file size {file.size}")
        LOG(f"message size {fileMetaData.get_size()}")

    def sendMetaDataOfAllFiles(self):
        for file_id in self.files:
            self.sendMetaData(file_id)
            sleep(0.1)
    
    def sendPartialFileContent(self, file_id):
        file                    = self.files[file_id]
        fileContent, file_index = file.getPartialFileContent()
        #log(f"File id {file_id} sending content of size {len(fileContent)}")
        self.msgcount += 1
        fileContentMessage = FileContent(file.id, fileContent, self.msgcount, file_index)
        #log(f"      File id {file_id} sending content of size {len(fileContent)} index{file_index}] with message count {self.msgcount}")
        self.connection.send(fileContentMessage)


    def HandleFileMetaDataMessage(self, message):
        file_name = message.get_file_name()
        file_path = self.file_directory + '/' + file_name
        file_path = file_utl.expand_path(file_path)
        self.files[message.file_id] = File(file_name, file_path, message.file_id)
        self.files[message.file_id].createFile()
        LOG(f"File meta data received for file id {message.file_id}, file name {file_name}, file path {file_path}, file size {message.file_size}")
        self.files[message.file_id].setFileSize(message.file_size)

    def HandleFileContentMessage(self, message):
        file = None
        try:
            file = self.files[message.file_id]
            #log(f"File id {message.file_id} received content of size {len(message.content_buffer)}, message id {message.msg_id}")
        except Exception as e:
            LOGE(f"Error handling file content message {e}, file id {message.file_id}")
            return
        #message.debug_print()
        file.writeContentToFile(message.get_content_buffer(), message.file_index)

    def sendFileContent(self, file_id):
        file = self.files[file_id]
        count = 0
        while file.file_index < file.size:
            self.sendPartialFileContent(file_id)
            #print(f"File id {file_id} {int((file.file_index / file.size) * 100)}% sent")
            count += 1
            sleep(0.01)
            if file.file_index >= file.size:
                LOG(f"File id {file_id} sent in {count} iterations with size {file.size} and file index {file.file_index} and file name {file.file_name}")
                break

    def sendAllFiles(self):
        self.sendMetaDataOfAllFiles()
        sleep(1)
        for file_id in self.files:
            self.sendFileContent(file_id)
            sleep(0.1)
        LOG("All files sent")
