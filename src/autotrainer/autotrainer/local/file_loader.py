
import os

def list_paths(directory_path: str, ext: str = ''):
    for file in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, file)) and file.endswith(ext):
            yield os.path.join(directory_path, file)

    