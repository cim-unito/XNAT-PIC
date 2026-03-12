from enum import Enum

class CustomFormLevel(Enum):
    PROJECT = "project"
    SUBJECT = "subject"
    EXPERIMENT = "experiment"

    def __str__(self) -> str:
        return self.value