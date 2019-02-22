from enum import Enum
# 'Multiclass or Multilabel'
class Container(Enum):
    train = "train"
    test = "test"
    holdout = "holdout"
    
    def __str__(self):
        return self.value

