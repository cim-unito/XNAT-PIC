import flet as ft


class ViewXnatAuth(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        self.txt_address = None
        self.txt_username = None
        self.txt_password = None
        self.ck_remember_user = None
        self.dlg = None

    def build_dialog(self, on_success, on_cancel):
        self._controller.set_remembered_credentials()

        self.txt_address = ft.TextField(
            label="XNAT address",
            value=self._controller.address or "",
        )
        self.txt_username = ft.TextField(
            label="Username",
            value=self._controller.username or "",
        )
        self.txt_password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            value=self._controller.password or "",
        )
        self.ck_remember_user = ft.Checkbox(
            label="Remember me",
            value=self._controller.remember or False,
        )

        btn_login = ft.ElevatedButton(
            "Login", on_click=self._controller.auth
        )
        btn_cancel = ft.TextButton(
            "Cancel", on_click=self._controller.cancel
        )

        self._controller.set_callbacks(on_success, on_cancel)

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("XNAT Login"),
            content=ft.Column(
                [
                    self.txt_address,
                    self.txt_username,
                    self.txt_password,
                    self.ck_remember_user,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[btn_cancel, btn_login],
        )

        return self.dlg

    def close_dialog(self):
        if self.dlg:
            self._page.close(self.dlg)
            self._page.update()

    def show_error(self, msg: str):
        dlg = ft.AlertDialog(title=ft.Text(msg))
        self._page.open(dlg)
        self._page.update()

    def set_controller(self, controller):
        self._controller = controller
