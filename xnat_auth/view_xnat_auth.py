import flet as ft

class ViewXnatAuth(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        # graphical elements
        self.txt_address = None
        self.txt_username = None
        self.txt_password = None
        self.ck_remember_user = None
        self.btn_login = None
        self.btn_cancel = None
        self.dlg_auth = None

    def build_dialog(self, on_success, on_cancel):
        """Create and return the authentication dialog."""
        self._build_controls(on_success, on_cancel)
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self.dlg_auth

    def set_initial_state(self):
        """Set initial state"""
        for ctrl in [
            self.txt_address,
            self.txt_username,
            self.txt_password,
            self.ck_remember_user,
            self.btn_login,
            self.btn_cancel,
        ]:
            ctrl.disabled = False

    def close_dialog(self):
        if self.dlg_auth:
            self._page.close(self.dlg_auth)
            self._page.update()

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

    def set_controller(self, controller):
        self._controller = controller

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, page):
        self._page = page

    def _build_controls(self, on_success, on_cancel):
        """Instantiate and configure all UI controls used by the dialog."""
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
        self.btn_login = ft.ElevatedButton(
            "Login",
        )
        self.btn_cancel = ft.TextButton(
            "Cancel",
        )

        self._controller.set_callbacks(on_success, on_cancel)

    def _bind_events(self):
        """Wire UI events to the controller callbacks."""
        self.btn_login.on_click = self._controller.auth
        self.btn_cancel.on_click = self._controller.cancel

    def _define_layout(self):
        """Define layout"""
        self.dlg_auth = ft.AlertDialog(
            modal=True,
            title=ft.Text("XNAT Login"),
            content=ft.Container(
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
                width=420,
            ),
            actions=[self.btn_cancel, self.btn_login],
        )


