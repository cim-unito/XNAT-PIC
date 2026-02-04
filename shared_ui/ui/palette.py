from dataclasses import dataclass
import flet as ft


@dataclass
class Palette:
    primary: str
    primary_hover: str
    primary_pressed: str
    primary_text: str
    surface: str
    surface_stronger: str
    subtle_text: str

def default_palette() -> Palette:
    return Palette(
        primary=ft.Colors.BLUE_600,
        primary_hover=ft.Colors.BLUE_700,
        primary_pressed=ft.Colors.BLUE_800,
        primary_text=ft.Colors.BLUE_900,
        surface=ft.Colors.BLUE_50,
        surface_stronger=ft.Colors.BLUE_100,
        subtle_text="#475569",
    )