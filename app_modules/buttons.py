import flet as ft

from app_modules.palette import Palette


class Buttons:

    @staticmethod
    def create_button_style(palette: Palette) -> ft.ButtonStyle:
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: palette.primary,
                ft.ControlState.HOVERED: palette.primary_hover,
                ft.ControlState.FOCUSED: palette.primary_hover,
                ft.ControlState.PRESSED: palette.primary_pressed,
                ft.ControlState.DISABLED: palette.surface_stronger,
            },
            color={
                ft.ControlState.DEFAULT: ft.Colors.WHITE,
                ft.ControlState.HOVERED: ft.Colors.WHITE,
                ft.ControlState.FOCUSED: ft.Colors.WHITE,
                ft.ControlState.PRESSED: ft.Colors.WHITE,
                ft.ControlState.DISABLED: ft.Colors.BLUE_300,
            },
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(16, 12, 16, 12),
            elevation=2,
            animation_duration=250,
        )