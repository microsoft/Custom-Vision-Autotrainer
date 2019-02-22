from enum import Enum
# 'Multiclass or Multilabel'
class ClassificationType(Enum):
    MULTICLASS = 'Multiclass'
    MULTILABEL = 'Multilabel'

    def __str__(self):
        return self.value
