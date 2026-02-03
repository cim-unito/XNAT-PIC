import flet as ft

from shared_ui.ui.palette import Palette


def build_section_card(
    title: str,
    description: str,
    icon: str,
    content: ft.Control,
    palette: Palette,
) -> ft.Control:
    return ft.Container(
        content=ft.Card(
            color=palette.surface,
            surface_tint_color=palette.primary,
            elevation=3,
            shape=ft.RoundedRectangleBorder(radius=18),
            content=ft.Container(
                padding=18,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=36,
                                    height=36,
                                    border_radius=10,
                                    bgcolor=palette.surface_stronger,
                                    alignment=ft.alignment.center,
                                    content=ft.Icon(
                                        icon,
                                        size=20,
                                        color=palette.primary,
                                    ),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            title,
                                            size=16,
                                            weight=ft.FontWeight.W_600,
                                            color=palette.primary_text,
                                            font_family="Inter",
                                        ),
                                        ft.Text(
                                            description,
                                            size=12,
                                            color=palette.subtle_text,
                                            font_family="Inter",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        content,
                    ],
                ),
            ),
        ),
    )