import flet as ft


class ViewMainInterface(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.subtitle = None
        self.btn_converter = None
        self.btn_uploader = None
        self.btn_custom_forms = None

    def build_interface(self):
        # Logo EuroBioimaging centrato in alto
        euro_logo = ft.Image(
            src="assets/images/EuroBioimaging.png",
            width=260,
            fit=ft.ImageFit.CONTAIN,
        )

        # Title (NON modificato nello stile)
        self._title = ft.Row(
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
        title_section = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self._title,
            ],
            spacing=0,
        )
        # Subtitle: layout più moderno (centrato, larghezza max, padding)
        self.subtitle = ft.Text(
            "Image dataset transfer to XNAT for preclinical imaging centers",
            size=21,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_700,
        )

        # Buttons (stile invariato)
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLUE_900,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20,  # aumento dimensione
        )

        self.btn_converter = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CHANGE_CIRCLE, size=26),
                    ft.Text("Converter", size=20),
                ],
            ),
            on_click=lambda _: self._controller.go_to_converter(),
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
            on_click=lambda _: self._controller.go_to_uploader(),
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
            on_click=lambda _: self._controller.go_to_custom_form(),
            style=btn_style,
            height=60,
        )
        # Bottoni centrati con spacing moderno
        buttons_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
            controls=[
                self.btn_converter,
                self.btn_uploader,
                self.btn_custom_forms,
            ],
        )

        # Loghi finali (centrati e ben distanziati)
        footer_logos = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src="assets/images/CNR.png", width=130,
                         fit=ft.ImageFit.CONTAIN),
                ft.Image(src="assets/images/IBB.png", width=140,
                         fit=ft.ImageFit.CONTAIN),
                ft.Image(src="assets/images/Unito.png", width=130,
                         fit=ft.ImageFit.CONTAIN),
            ],
        )

        # Layout generale: tutto centrato, con spacing verticale moderno
        return ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        euro_logo,
                        ft.Container(height=20),
                        title_section,
                        self.subtitle,
                        ft.Container(height=30),
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
