import flet as ft

from shared_ui.ui.palette import Palette


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