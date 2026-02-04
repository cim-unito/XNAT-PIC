import flet as ft

from shared_ui.ui.palette import Palette


class Button:

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

    @staticmethod
    def build_text_button(
        label: str,
        style: ft.ButtonStyle,
        *,
        tooltip: str | None = None,
        expand: bool = True,
        icon: ft.Control | None = None,
        text_control: ft.Text | None = None,
    ) -> ft.ElevatedButton:
        controls = []
        if icon is not None:
            controls.append(icon)
        if text_control is None:
            text_control = ft.Text(
                value=label,
                size=16,
                weight=ft.FontWeight.W_600,
                font_family="Inter",
            )
        controls.append(text_control)
        return ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=controls,
            ),
            tooltip=tooltip,
            style=style,
            expand=expand,
        )