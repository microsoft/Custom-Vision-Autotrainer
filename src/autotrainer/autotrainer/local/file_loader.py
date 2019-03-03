
import os

def list_paths(directory_path: str, ext: str = ''):
    for file in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, file)) and file.endswith(ext):
            yield os.path.join(directory_path, file)


def list_yolo_annotation_paths(annotation_path: str, image_paths: [str]):
    annotations = []
    for path in image_paths:
        filename = os.path.splitext(os.path.basename(path))[0]
        loc = os.path.join(annotation_path, filename + ".txt")
        annotations.append(loc)
    return annotations
