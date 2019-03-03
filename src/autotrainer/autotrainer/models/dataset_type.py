from enum import Enum


class DatasetType(Enum):
    yolo = "yolo"
    generic = "generic"

    def __str__(self):
        return self.value
