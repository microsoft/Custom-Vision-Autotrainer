from enum import Enum

class Domain(Enum):
    GENERAL_CLASSIFICATION = 'general'
    GENERAL_CLASSIFICATION_COMPACT = 'general-compact'
    GENERAL_OBJECT_DETECTION = 'general-obj-detection'
    FOOD_CLASSIFICATION = 'food'

    def __str__(self):
        return self.value


def to_domain_id(domain: Domain)-> str:
    if domain == Domain.GENERAL_CLASSIFICATION:
        return "ee85a74c-405e-4adc-bb47-ffa8ca0c9f31"
    if domain == Domain.GENERAL_CLASSIFICATION_COMPACT:
        return "0732100f-1a38-4e49-a514-c9b44c697ab5"
    if domain == Domain.FOOD_CLASSIFICATION :
        return "c151d5b5-dd07-472a-acc8-15d29dea8518"
    if domain == Domain.GENERAL_OBJECT_DETECTION:
        return "a27d5ca5-bb19-49d8-a70a-fec086c47f5b"
    else:
        return None
