class AuthDialogMixin:
    def __init__(self):
        self._page = None
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