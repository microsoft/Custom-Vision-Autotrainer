
from enum import Enum

class Platform(Enum):
    DOCKER = "DockerFile"
    CORE_ML = "CoreML"
    TENSORFLOW = "TensorFlow"
    ONNX = "ONNX"

    def __str__(self):
        return self.value



class Flavour(Enum):
    Linux = "Linux"
    Windows = "Windows"
    ONNX10 = "ONNX10"
    ONNX12 = "ONNX12"

    def __str__(self):
        return self.value


