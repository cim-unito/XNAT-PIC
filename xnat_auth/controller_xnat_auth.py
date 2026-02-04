from xnat_client.xnat_session import XnatSession


class ControllerXnatAuth:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._address = None
        self._username = None
        self._password = None
        self._remember = None

        self._on_success = None
        self._on_cancel = None

    def set_callbacks(self, on_success, on_cancel):
        self._on_success = on_success
        self._on_cancel = on_cancel

    def auth(self, e):
        self._update_fields_from_view()

        xnat_session = XnatSession(self._address,
                                   self._username,
                                   self._password)
        if xnat_session.connect():
            self._model.persist_credentials(
                self._address,
                self._username,
                self._password,
                self._remember,
            )
            self._view.close_dialog()
            if self._on_success:
                self._on_success(xnat_session)
        else:
            self._view.create_alert("Connection failed.")
            self._view.close_dialog()
            if self._on_cancel:
                self._on_cancel()

    def cancel(self, e):
        self._view.close_dialog()
        if self._on_cancel:
            self._on_cancel()

    def set_remembered_credentials(self):
        remembered = self._model.load_remembered_credential()
        if remembered:
            self._address = remembered.address
            self._username = remembered.username
            self._password = remembered.password
            self._remember = remembered.remember
        else:
            self._address = None
            self._username = None
            self._password = None
            self._remember = None

    @property
    def address(self):
        return self._address

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def remember(self):
        return self._remember

    def _update_fields_from_view(self):
        self._address = self._view.txt_address.value
        self._username = self._view.txt_username.value
        self._password = self._view.txt_password.value
        self._remember = self._view.ck_remember_user.value