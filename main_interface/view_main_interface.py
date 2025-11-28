import flet as ft


class ViewMainInterface(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None

        # ----- Graphical elements -----
        self.img_eurobioimaging = None
        self.title = None
        self.subtitle = None
        self.btn_converter = None
        self.btn_uploader = None
        self.btn_custom_forms = None
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
        # button style
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLUE_900,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
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
                ft.Text(
                    "XNAT-PIC",
                    size=50,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # subtitle
        self.subtitle = ft.Text(
            "Image dataset transfer to XNAT for preclinical imaging centers",
            size=21,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_700,
        )

        # buttons converter, uploader, custom form
        self.btn_converter = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CHANGE_CIRCLE, size=26),
                    ft.Text("Converter", size=20),
                ],
            ),
            style=btn_style,
            height=60,
        )

        self.btn_uploader = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CLOUD_UPLOAD, size=26),
                    ft.Text("Uploader", size=20),
                ],
            ),
            style=btn_style,
            height=60,
        )

        self.btn_custom_forms = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.DATASET, size=26),
                    ft.Text("Custom Form", size=20),
                ],
            ),
            style=btn_style,
            height=60,
        )

        self.img_cnr = ft.Image(src="assets/images/CNR.png", width=130,
                                fit=ft.ImageFit.CONTAIN)
        self.img_ibb = ft.Image(src="assets/images/IBB.png", width=140,
                                fit=ft.ImageFit.CONTAIN)
        self.img_unito = ft.Image(src="assets/images/Unito.png", width=130,
                                  fit=ft.ImageFit.CONTAIN)

    def _bind_events(self):
        """Bind events"""
        self.btn_converter.on_click = lambda \
                _: self._controller.go_to_converter()
        self.btn_uploader.on_click = lambda \
                _: self._controller.go_to_uploader()
        self.btn_custom_forms.on_click = lambda \
                _: self._controller.go_to_custom_form()

    def _define_layout(self):
        """Define layout"""
        buttons_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
            controls=[
                self.btn_converter,
                self.btn_uploader,
                self.btn_custom_forms,
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

        self._main_layout = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        self.img_eurobioimaging,
                        self.title,
                        self.subtitle,
                        buttons_row,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    footer_logos,
                    padding=20,
                ),
            ],
            expand=True,
        )

    # ------------------------------------------------------
    # INITIAL STATE
    # ------------------------------------------------------
    def set_initial_state(self):
        """Set initial state"""
        self.btn_converter.disabled = False
        self.btn_uploader.disabled = False
        self.btn_custom_forms.disabled = False

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

    @page.setter
    def page(self, page):
        self._page = page

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()
