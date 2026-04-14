from enum import Enum

class DicomModality(Enum):
    MR = "mr"
    US = "us"
    OI = "oi"
    PAI = "pai"

    def __str__(self) -> str:
        return self.value
