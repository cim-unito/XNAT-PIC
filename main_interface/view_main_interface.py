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
        primary = ft.Colors.BLUE_700
        secondary = ft.Colors.BLUE_300
        surface = ft.Colors.BLUE_50

        # button style
        btn_style = ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_500,
                ft.ControlState.HOVERED: ft.Colors.BLUE_600,
                ft.ControlState.FOCUSED: ft.Colors.BLUE_700,
            },
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=14),
            padding=ft.Padding(14, 12, 14, 12),
            elevation=4,
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
                        size=50,
                        weight=ft.FontWeight.BOLD,
                        color=primary,
                    ),
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    border_radius=20,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # subtitle
        self.subtitle = ft.Text(
            "Image dataset transfer to XNAT for preclinical imaging centers",
            size=21,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_800,
        )

        # buttons converter, uploader, custom form
        self.btn_converter = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CHANGE_CIRCLE_OUTLINED, size=26),
                    ft.Text("Converter", size=18, weight=ft.FontWeight.W_600),
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
                    ft.Text("Uploader", size=18, weight=ft.FontWeight.W_600),
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
                    ft.Text("Custom Form", size=18, weight=ft.FontWeight.W_600),
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
            surface=surface,
        )
        self.uploader_card = self._build_action_card(
            title="Upload to XNAT",
            description="Send validated data to XNAT with progress feedback and retries.",
            icon=ft.Icons.CLOUD_SYNC,
            button=self.btn_uploader,
            primary=primary,
            surface=surface,
        )
        self.custom_form_card = self._build_action_card(
            title="Custom data forms",
            description="Design metadata forms to keep submissions consistent across teams.",
            icon=ft.Icons.DASHBOARD_OUTLINED,
            button=self.btn_custom_form,
            primary=primary,
            surface=surface,
        )

        self.img_cnr = ft.Image(src="assets/images/CNR.png", width=130,
                                fit=ft.ImageFit.CONTAIN)
        self.img_ibb = ft.Image(src="assets/images/IBB.png", width=140,
                                fit=ft.ImageFit.CONTAIN)
        self.img_unito = ft.Image(src="assets/images/Unito.png", width=130,
                                  fit=ft.ImageFit.CONTAIN)

    def _build_action_card(self, title, description, icon, button, primary, surface):
        """Reusable modern card for each main action."""
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            padding=18,
            bgcolor=surface,
            border=ft.border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.BLUE_200)),
            border_radius=20,
            ink=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.18, ft.Colors.BLUE_700),
            ),
            content=ft.Column(
                spacing=14,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        bgcolor=ft.Colors.with_opacity(0.15, primary),
                        border_radius=50,
                        content=ft.Icon(icon, size=26, color=primary),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Text(
                        description,
                        size=14,
                        color=ft.Colors.BLUE_800,
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
                spacing=10,
                controls=[
                    self.img_eurobioimaging,
                    self.title,
                    self.subtitle,
                ],
            ),
            padding=ft.padding.symmetric(vertical=10),
        )

        cards_area = ft.Container(
            content=ft.Column(
                spacing=18,
                controls=[
                    ft.Row(
                        [
                            ft.Text(
                                "Quick actions",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_900,
                            ),
                            ft.Text(
                                "Choose the task you want to perform.",
                                size=14,
                                color=ft.Colors.BLUE_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    buttons_row,
                ],
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLUE_50),
            border_radius=18,
        )

        self._main_layout = ft.Container(
            expand=True,
            padding=ft.padding.all(24),
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