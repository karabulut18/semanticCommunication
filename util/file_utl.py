import os

def get_file_size(file_path):
    return os.path.getsize(file_path)

def expand_path(path):
    return os.path.expanduser(path)

def file_exists(file_path):
    return os.path.exists(file_path)

def create_dir(dir_path):
    os.makedirs(dir_path, exist_ok=True)

def get_file_name(file_path):
    return os.path.basename(file_path)

def create_symbolic_link(src, dst):
    if os.path.islink(dst):
        os.unlink(dst)  # Remove the existing symbolic link
    os.symlink(src, dst)

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

def get_parent_dir(dir_path):
    return os.path.dirname(dir_path)

def remove_file(file_path):
    os.remove(file_path)

def remove_dir(dir_path):
    os.rmdir(dir_path)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def get_files_in_dir(dir_path):
    return os.listdir(dir_path)

def read_file_with_start_end_index(file_path, start, end):
    with open(file_path, 'r') as file:
        file.seek(start)
        return file.read(end - start)

def read_binary_file_with_start_end_index(file_path, start, end):
    with open(file_path, 'rb') as file:
        file_size = os.path.getsize(file_path)
        if start > file_size:
            raise ValueError("Start index is beyond file size.")
        file.seek(start)
        fileContent = file.read(min(end, file_size) - start)
        return fileContent

def write_to_file_with_start_index(file_path, content, start):
    with open(file_path, 'r+b') as file:  # 'r+b' to modify part of the file
        file.seek(start)
        file.write(content)

def create_file(file_path):
    if file_exists(file_path):
        return False
    try:
        with open(file_path, 'w') as file:
            pass
        return True
    except:
        return False


def get_working_directory():
    return os.getcwd()

def convert_relative_path_to_absolute_path(relative_path):
    return os.path.abspath(relative_path)
