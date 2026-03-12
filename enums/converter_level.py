from enum import Enum

class ConverterLevel(Enum):
    PROJECT = "project"
    SUBJECT = "subject"
    EXPERIMENT = "experiment"

    def __str__(self) -> str:
        return self.value
