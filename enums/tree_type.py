from enum import Enum

class TreeType(Enum):
    RAW = "raw"
    DICOM = "dicom"

    def __str__(self) -> str:
        return self.value