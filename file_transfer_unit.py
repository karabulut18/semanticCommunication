import file_utl as file_utl
from file import File
from time import sleep
from logger import LOG, LOGE, LOGD
from fileMetaData import FileMetaData
from fileContent import FileContent

MAX_FILE_SIZE = 1024 * 1024 * 10

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
            sleep(0.2)
            self.sendMetaData(file_id)
            
    def sendPartialFileContent(self, file_id):
        file                    = self.files[file_id]
        fileContent, file_index = file.getPartialFileContent()
        #log(f"File id {file_id} sending content of size {len(fileContent)}")
        self.msgcount += 1
        fileContentMessage = FileContent(file.id, fileContent, self.msgcount, file_index)
        #log(f"      File id {file_id} sending content of size {len(fileContent)} index{file_index}] with message count {self.msgcount}")
        self.connection.send(fileContentMessage)


    def CreateFileForWriting(self, file_id, file_size, file_name):
        file_path = self.file_directory + '/' + file_name
        file_path = file_utl.expand_path(file_path)
        self.files[file_id] = File(file_name, file_path, file_id)
        self.files[file_id].createFile()
        self.files[file_id].setFileSize(file_size)
        LOG(f"File created for writing with file id {file_id}, file name {file_name}, file path {file_path}, file size {file_size}")


    def HandleFileMetaDataMessage(self, message):
        file_name = message.get_file_name()
        self.CreateFileForWriting(message.file_id, message.file_size, file_name)
        LOG(f"File meta data received for file id {message.file_id}, file name {file_name}, file size {message.file_size}")


    def HandleFileContentMessage(self, message):
        file = None
        try:
            file = self.files[message.file_id]
            if file is None:
                # if file is none, create a new file object
                file_name = f"file_{message.file_id}.out"
                self.CreateFileForWriting(message.file_id, MAX_FILE_SIZE, file_name)
                file = self.files[message.file_id]
                LOGD(f"File id {message.file_id} created for writing")
            LOGD(f"message id {message.msg_id}")
        
        except Exception as e:
            LOGE(f"Error handling file content message error {e}, file id {message.file_id}")
            message.debug_print()
            return
        file.writeContentToFile(message.get_content_buffer(), message.file_index)

    def sendFileContent(self, file_id):
        file = self.files[file_id]
        count = 0
        while file.file_index < file.size and self.connection.running:
            self.sendPartialFileContent(file_id)
            #print(f"File id {file_id} {int((file.file_index / file.size) * 100)}% sent")
            count += 1
            sleep(0.1)
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
        print("All files sent")
