from enum import Enum

class UploaderLevel(Enum):
    PROJECT = "project"
    SUBJECT = "subject"
    EXPERIMENT = "experiment"
    FILE = "file"

    def __str__(self) -> str:
        return self.value
