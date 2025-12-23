import flet as ft


class ViewMainInterface(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self.img_eurobioimaging = None
        self.title = None
        self.subtitle = None
        self.btn_converter = None
        self.btn_uploader = None
        self.btn_custom_form = None
        self.converter_card = None
        self.uploader_card = None
        self.custom_form_card = None
        self.img_cnr = None
        self.img_ibb = None
        self.img_unito = None

        # layout
        self._main_layout = None

    # ------------------------------------------------------
    # BUILD MAIN INTERFACE
    # -----------------------------------------------------
    def build_interface(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self._main_layout

    def _build_controls(self):
        """Graphical elements"""
        # shared colors for the blue / light-blue palette
        primary = ft.Colors.BLUE_600
        primary_hover = ft.Colors.BLUE_700
        primary_pressed = ft.Colors.BLUE_800
        primary_text = ft.Colors.BLUE_900
        surface = ft.Colors.BLUE_50
        surface_stronger = ft.Colors.BLUE_100
        subtle_text = "#475569"

        # button style
        btn_style = ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: primary,
                ft.ControlState.HOVERED: primary_hover,
                ft.ControlState.FOCUSED: primary_hover,
                ft.ControlState.PRESSED: primary_pressed,
                ft.ControlState.DISABLED: surface_stronger,
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

        # image EuroBioimaging
        self.img_eurobioimaging = ft.Image(
            src="assets/images/EuroBioimaging.png",
            width=260,
            fit=ft.ImageFit.CONTAIN,
        )

        # title
        self.title = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "XNAT-PIC",
                        size=24,
                        weight=ft.FontWeight.W_600,
                        color=primary_text,
                        font_family="Inter",
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border_radius=16,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # subtitle
        self.subtitle = ft.Text(
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

        self.converter_card = self._build_action_card(
            title="Convert your datasets",
            description="Transform image data with presets and quality checks before sharing.",
            icon=ft.Icons.AUTO_FIX_HIGH,
            button=self.btn_converter,
            primary=primary,
            primary_text=primary_text,
            subtle_text=subtle_text,
            surface=surface,
            surface_stronger=surface_stronger,
        )
        self.uploader_card = self._build_action_card(
            title="Upload to XNAT",
            description="Send validated data to XNAT with progress feedback and retries.",
            icon=ft.Icons.CLOUD_SYNC,
            button=self.btn_uploader,
            primary=primary,
            primary_text=primary_text,
            subtle_text=subtle_text,
            surface=surface,
            surface_stronger=surface_stronger,
        )
        self.custom_form_card = self._build_action_card(
            title="Custom data forms",
            description="Design metadata forms to keep submissions consistent across teams.",
            icon=ft.Icons.DASHBOARD_OUTLINED,
            button=self.btn_custom_form,
            primary=primary,
            primary_text=primary_text,
            subtle_text=subtle_text,
            surface=surface,
            surface_stronger=surface_stronger,
        )

        self.img_cnr = ft.Image(src="assets/images/CNR.png", width=130,
                                fit=ft.ImageFit.CONTAIN)
        self.img_ibb = ft.Image(src="assets/images/IBB.png", width=140,
                                fit=ft.ImageFit.CONTAIN)
        self.img_unito = ft.Image(src="assets/images/Unito.png", width=130,
                                  fit=ft.ImageFit.CONTAIN)


    def _build_action_card(
            self,
            title,
            description,
            icon,
            button,
            primary,
            primary_text,
            subtle_text,
            surface,
            surface_stronger,
    ):
        """Reusable modern card for each main action."""
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            padding=20,
            bgcolor=surface,
            border=ft.border.all(1, surface_stronger),
            border_radius=18,
            ink=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.14, primary),
            ),
            content=ft.Column(
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        bgcolor=surface_stronger,
                        border_radius=12,
                        content=ft.Icon(icon, size=24, color=primary),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=primary_text,
                        font_family="Inter",
                    ),
                    ft.Text(
                        description,
                        size=13,
                        color=subtle_text,
                        font_family="Inter",
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row([
                        ft.Container(
                            content=button,
                            alignment=ft.alignment.center_left,
                        ),
                    ]),
                ],
            ),
        )

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
                self.converter_card,
                self.uploader_card,
                self.custom_form_card,
            ],
        )

        footer_logos = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.img_cnr,
                self.img_ibb,
                self.img_unito,
            ],
        )

        hero = ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    self.img_eurobioimaging,
                    self.title,
                    self.subtitle,
                ],
            ),
            padding=ft.padding.symmetric(vertical=16),
        )

        cards_area = ft.Container(
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        [
                            ft.Text(
                                "Quick actions",
                                size=18,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.BLUE_900,
                                font_family="Inter",
                            ),
                            ft.Text(
                                "Choose the task you want to perform.",
                                size=14,
                                color="#475569",
                                font_family="Inter",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    buttons_row,
                ],
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_50),
            border_radius=20,
        )

        self._main_layout = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=28, vertical=18),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    hero,
                    cards_area,
                    ft.Container(
                        footer_logos,
                        padding=20,
                    ),
                ],
                expand=True,
            ),
        )

    # ------------------------------------------------------
    # INITIAL STATE
    # ------------------------------------------------------
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
