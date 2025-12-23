import flet as ft

from app_modules.palette import Palette
from app_modules.buttons import Buttons


class ViewMainInterface(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self.img_eurobioimaging = None
        self.row_title = None
        self.txt_subtitle = None
        self.btn_converter = None
        self.btn_uploader = None
        self.btn_custom_form = None
        self.card_converter = None
        self.card_uploader = None
        self.card_custom_form = None
        self.img_cnr = None
        self.img_ibb = None
        self.img_unito = None

        # layout
        self._main_layout = None

        # palette
        self.palette = self._create_default_palette()

    # ------------------------------------------------------
    # BUILD MAIN INTERFACE
    # -----------------------------------------------------
    def build_interface(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()

        return self._main_layout

    def set_initial_state(self):
        """Set initial state"""
        self.btn_converter.disabled = False
        self.btn_uploader.disabled = False
        self.btn_custom_form.disabled = False

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    @property
    def page(self):
        return self._page

    def _build_controls(self):
        """Graphical elements"""
        btn_style = Buttons().create_button_style(self.palette)

        # logo eurobioimaging
        self.img_eurobioimaging = ft.Image(
            src="assets/images/EuroBioimaging.png",
            width=380,
            fit=ft.ImageFit.CONTAIN,
        )

        # title
        self.row_title = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "XNAT-PIC",
                        size=36,
                        weight=ft.FontWeight.W_700,
                        color=self.palette.primary_text,
                        font_family="Inter",
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    border_radius=18,
                    #bgcolor=self.palette.surface,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # subtitle
        self.txt_subtitle = ft.Text(
            "Image dataset transfer to XNAT for preclinical imaging centers",
            size=15,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_700,
            font_family="Inter",
        )

        # buttons converter, uploader, custom form
        self.btn_converter = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CHANGE_CIRCLE_OUTLINED, size=26),
                    ft.Text("Converter", size=16, weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            height=52,
            tooltip="Convert imaging datasets with guided steps",
        )

        self.btn_uploader = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CLOUD_UPLOAD, size=26),
                    ft.Text("Uploader", size=16, weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            height=52,
            tooltip="Upload converted data directly to XNAT",
        )

        self.btn_custom_form = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.TABLE_ROWS, size=26),
                    ft.Text("Custom Form", size=16, weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            height=52,
            tooltip="Create and manage tailored data forms",
        )

        # card converter, uploader, custom form
        self.card_converter = self._build_action_card(
            title="Convert your datasets",
            description="Transform image data with presets and quality checks before sharing.",
            icon=ft.Icons.AUTO_FIX_HIGH,
            button=self.btn_converter,
            palette=self.palette,
        )
        self.card_uploader = self._build_action_card(
            title="Upload to XNAT",
            description="Send validated data to XNAT with progress feedback and retries.",
            icon=ft.Icons.CLOUD_SYNC,
            button=self.btn_uploader,
            palette=self.palette,
        )
        self.card_custom_form = self._build_action_card(
            title="Custom data forms",
            description="Design metadata forms to keep submissions consistent across teams.",
            icon=ft.Icons.DASHBOARD_OUTLINED,
            button=self.btn_custom_form,
            palette=self.palette,
        )

        self.img_cnr = ft.Image(src="assets/images/CNR.png", width=110,
                                fit=ft.ImageFit.CONTAIN)
        self.img_ibb = ft.Image(src="assets/images/IBB.png", width=110,
                                fit=ft.ImageFit.CONTAIN)
        self.img_unito = ft.Image(src="assets/images/Unito.png", width=110,
                                  fit=ft.ImageFit.CONTAIN)

    def _bind_events(self):
        """Bind events"""
        self.btn_converter.on_click = lambda \
                _: self._controller.go_to_converter()
        self.btn_uploader.on_click = lambda \
                _: self._controller.go_to_uploader()
        self.btn_custom_form.on_click = lambda \
                _: self._controller.go_to_custom_form()

    def _define_layout(self):
        """Define layout"""
        buttons_row = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=18,
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                self.card_converter,
                self.card_uploader,
                self.card_custom_form,
            ],
        )

        footer_logos = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=32,
            spacing=28,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(self.img_cnr, col={"xs": 12, "sm": 4},
                             alignment=ft.alignment.center),
                ft.Container(self.img_ibb, col={"xs": 12, "sm": 4},
                             alignment=ft.alignment.center),
                ft.Container(self.img_unito, col={"xs": 12, "sm": 4},
                             alignment=ft.alignment.center),
            ],
        )

        hero_section = ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    self.img_eurobioimaging,
                    self.row_title,
                    self.txt_subtitle,
                ],
            ),
            padding=ft.padding.symmetric(vertical=16),
        )

        self._main_layout = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=28, vertical=18),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    hero_section,
                    buttons_row,
                    ft.Container(
                        footer_logos,
                        padding=ft.padding.symmetric(vertical=12),
                    ),
                ],
                expand=True,
            ),
        )

    @staticmethod
    def _create_default_palette() -> Palette:
        return Palette(
            primary=ft.Colors.BLUE_600,
            primary_hover=ft.Colors.BLUE_700,
            primary_pressed=ft.Colors.BLUE_800,
            primary_text=ft.Colors.BLUE_900,
            surface=ft.Colors.BLUE_50,
            surface_stronger=ft.Colors.BLUE_100,
            subtle_text="#475569",
        )

    @staticmethod
    def _build_action_card(
            title: str,
            description: str,
            icon: str,
            button: ft.Control,
            palette: Palette,
    ) -> ft.Control:
        """Define card for each main action."""
        card_content = ft.Container(
            padding=20,
            content=ft.Column(
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        bgcolor=palette.surface_stronger,
                        border_radius=12,
                        content=ft.Icon(icon, size=24, color=palette.primary),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=palette.primary_text,
                        font_family="Inter",
                    ),
                    ft.Text(
                        description,
                        size=13,
                        color=palette.subtle_text,
                        font_family="Inter",
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Container(
                        content=button,
                        alignment=ft.alignment.center_left,
                    ),
                ],
            ),
        )

        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            content=ft.Card(
                content=card_content,
                color=palette.surface,
                surface_tint_color=palette.primary,
                elevation=3,
                shape=ft.RoundedRectangleBorder(radius=18),
            ),
        )