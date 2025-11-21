from dataclasses import dataclass


@dataclass
class XnatCredentialDto:
    address: str
    username: str
    password: str
    remember: bool

def __str__(self):
    return f"{self.address} {self.username} {'*' * len(self.password)}"
