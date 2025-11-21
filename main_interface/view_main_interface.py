import flet as ft


class ViewMainInterface(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.btn_converter = None
        self.btn_uploader = None
        self.btn_custom_forms = None

    def build_interface(self):
        # Define controls
        # title
        self._title = ft.Text("XNAT-PIC", color="blue", size=24)

        # buttons
        self.btn_converter = ft.ElevatedButton(
            text="Converter",
            on_click=lambda _: self._controller.go_to_converter(),
        )
        self.btn_uploader = ft.ElevatedButton(
            text="Uploader",
            on_click=lambda _: self._controller.go_to_uploader(),
        )
        self.btn_custom_forms = ft.ElevatedButton(
            text="Custom Forms", on_click=lambda _: self._controller.go_to_custom_forms()
        )

        # Define layout
        row1 = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.btn_converter,
                self.btn_uploader,
                self.btn_custom_forms,
            ],
        )

        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[self._title, row1],
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
