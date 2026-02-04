import flet as ft

from shared_ui.ui.palette import Palette


class Button:

    DEFAULT_FONT = "Inter"
    DEFAULT_TEXT_SIZE = 16
    DEFAULT_TEXT_WEIGHT = ft.FontWeight.W_600
    DEFAULT_ICON_TEXT_SPACING = 10
    DEFAULT_RADIUS = 12
    DEFAULT_PADDING = ft.Padding(16, 12, 16, 12)
    DEFAULT_ELEVATION = 2
    DEFAULT_ANIMATION_DURATION = 250

    @staticmethod
    def create_button_style(
        palette: Palette,
        *,
        radius: int = DEFAULT_RADIUS,
        padding: ft.Padding = DEFAULT_PADDING,
        elevation: int = DEFAULT_ELEVATION,
        animation_duration: int = DEFAULT_ANIMATION_DURATION,
        text_color: str = ft.Colors.WHITE,
        disabled_text_color: str = ft.Colors.BLUE_300,
        bgcolor: dict[ft.ControlState, str] | None = None,
        color: dict[ft.ControlState, str] | None = None,
    ) -> ft.ButtonStyle:
        if bgcolor is None:
            bgcolor = {
                ft.ControlState.DEFAULT: palette.primary,
                ft.ControlState.HOVERED: palette.primary_hover,
                ft.ControlState.FOCUSED: palette.primary_hover,
                ft.ControlState.PRESSED: palette.primary_pressed,
                ft.ControlState.DISABLED: palette.surface_stronger,
            },
        if color is None:
            color = {
                ft.ControlState.DEFAULT: text_color,
                ft.ControlState.HOVERED: text_color,
                ft.ControlState.FOCUSED: text_color,
                ft.ControlState.PRESSED: text_color,
                ft.ControlState.DISABLED: disabled_text_color,
            }
        return ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
            shape=ft.RoundedRectangleBorder(radius=radius),
            padding=padding,
            elevation=elevation,
            animation_duration=animation_duration,
        )

    @staticmethod
    def build_text_button(
        label: str | None,
        style: ft.ButtonStyle,
        *,
        tooltip: str | None = None,
        expand: bool = True,
        icon: ft.Control | None = None,
        text_control: ft.Text | None = None,
        on_click: ft.ControlEventType | None = None,
        disabled: bool = False,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
        spacing: int = DEFAULT_ICON_TEXT_SPACING,
        text_size: int = DEFAULT_TEXT_SIZE,
        text_weight: ft.FontWeight = DEFAULT_TEXT_WEIGHT,
        font_family: str = DEFAULT_FONT,
    ) -> ft.ElevatedButton:
        if label is None and text_control is None:
            raise ValueError("label or text_control must be provided")
        content = Button._build_content(
            label=label,
            icon=icon,
            text_control=text_control,
            alignment=alignment,
            spacing=spacing,
            text_size=text_size,
            text_weight=text_weight,
            font_family=font_family,
        )
        return ft.ElevatedButton(
            content=content,
            tooltip=tooltip,
            style=style,
            expand=expand,
            on_click=on_click,
            disabled=disabled,
        )

    @staticmethod
    def _build_content(
        *,
        label: str | None,
        icon: ft.Control | None,
        text_control: ft.Text | None,
        alignment: ft.MainAxisAlignment,
        spacing: int,
        text_size: int,
        text_weight: ft.FontWeight,
        font_family: str,
    ) -> ft.Row:
        controls: list[ft.Control] = []
        if icon is not None:
            controls.append(icon)
        if text_control is None:
            text_control = ft.Text(
                value=label,
                size=text_size,
                weight=text_weight,
                font_family=font_family,
            )
        controls.append(text_control)
        return ft.Row(
            alignment=alignment,
            spacing=spacing,
            controls=controls,
        )