import flet as ft

from shared_ui.ui.palette import Palette


def build_header(
    title: str,
    icon: str,
    palette: Palette,
) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=16,
                    bgcolor=palette.surface_stronger,
                    alignment=ft.alignment.center,
                    content=ft.Icon(
                        icon,
                        size=30,
                        color=palette.primary,
                    ),
                ),
                ft.Text(
                    value=title,
                    size=32,
                    weight=ft.FontWeight.W_700,
                    color=palette.primary_text,
                    font_family="Inter",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        ),
        bgcolor=palette.surface,
        padding=ft.padding.symmetric(horizontal=18, vertical=12),
        border_radius=20,
    )