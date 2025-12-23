from dataclasses import dataclass


@dataclass
class Palette:
    primary: str
    primary_hover: str
    primary_pressed: str
    primary_text: str
    surface: str
    surface_stronger: str
    subtle_text: str