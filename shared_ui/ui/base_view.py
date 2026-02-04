import flet as ft


class BaseView(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None
        self._dlg_auth = None

    def open_auth_dialog(self, dlg):
        self._dlg_auth = dlg
        self._page.open(dlg)
        self._page.update()

    def close_auth_dialog(self):
        if self._dlg_auth:
            self._page.close(self._dlg_auth)
            self._dlg_auth = None
            self._page.update()

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

    def open_directory_picker(self):
        if getattr(self, "file_picker", None):
            self.file_picker.get_directory_path()

    def set_home_back_state(self, label, icon, enabled=True):
        if getattr(self, "txt_home_back", None):
            self.txt_home_back.value = label
        if getattr(self, "icon_home_back", None):
            self.icon_home_back.name = icon
        if getattr(self, "btn_home_back", None):
            self.btn_home_back.disabled = not enabled

    @staticmethod
    def set_controls_disabled(controls, disabled=True):
        for control in controls:
            if control is not None:
                control.disabled = disabled

    def set_controls_enabled(self, controls):
        self.set_controls_disabled(controls, disabled=False)

    @staticmethod
    def reset_dropdowns(dropdowns, reset_options=True):
        for dd in dropdowns:
            if reset_options:
                dd.options = []
            dd.key = "Select"
            dd.value = None

    @staticmethod
    def reset_dropdown(dropdown):
        if dropdown is None:
            return
        dropdown.options = []
        dropdown.value = None

    @staticmethod
    def populate_dropdown(dropdown, items, key_field="id", text_field="label"):
        if dropdown is None:
            return
        dropdown.options = [
            ft.dropdown.Option(key=item[key_field], text=item[text_field])
            for item in items
        ]
        dropdown.value = None

    def apply_view_state(
        self,
        enable_controls=(),
        disable_controls=(),
        home_back_label=None,
        home_back_icon=None,
        home_back_enabled=None,
    ):
        self.set_controls_enabled(enable_controls)
        self.set_controls_disabled(disable_controls, disabled=True)
        if home_back_label or home_back_icon or home_back_enabled is not None:
            self.set_home_back_state(
                home_back_label or self.txt_home_back.value,
                home_back_icon or self.icon_home_back.name,
                enabled=True if home_back_enabled is None else home_back_enabled,
            )

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

    def set_controller(self, controller):
        self._controller = controller