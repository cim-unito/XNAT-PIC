from typing import Callable, Optional

from uploader.model_xnat_new_project import ModelXnatNewProject


class ControllerXnatNewProject:
    """
    Controller per la dialog "New Project".
    """

    def __init__(self, view, model: ModelXnatNewProject):
        self._view = view
        self._model = model

        # callback impostate dal chiamante (es. ControllerUploader)
        self._on_created: Optional[Callable[[str, str], None]] = None  # (project_id, label)
        self._on_cancel: Optional[Callable[[], None]] = None

    # --------------------------------------------------
    # CALLBACK ESTERNE
    # --------------------------------------------------
    def set_callbacks(
        self,
        on_created: Callable[[str, str], None],
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        self._on_created = on_created
        self._on_cancel = on_cancel

    # --------------------------------------------------
    # EVENTI UI: CAMPI
    # --------------------------------------------------
    def on_title_changed(self, value: str):
        d = self._model.data
        d.title = value
        # Se ID non è editabile, lo seguiamo dal title
        if not d.editable_id:
            d.project_id = value
            self._view.set_project_id_value(value)
        self._update_can_submit()

    def on_project_id_changed(self, value: str):
        d = self._model.data
        d.project_id = value
        self._update_can_submit()

    def on_toggle_edit_id(self, editable: bool):
        d = self._model.data
        d.editable_id = editable
        self._view.set_project_id_editable(editable)
        # se torna non editabile → resync con title
        if not editable:
            d.project_id = d.title
            self._view.set_project_id_value(d.title)
        self._update_can_submit()

    def on_access_changed(self, value: str):
        self._model.data.access_status = value

    def on_description_changed(self, value: str):
        self._model.data.description = value

    def on_add_keyword(self, kw: str):
        kw = kw.strip()
        if kw and kw not in self._model.data.keywords:
            self._model.data.keywords.append(kw)
            self._view.update_keywords(self._model.data.keywords)

    def on_remove_keyword(self, kw: str):
        if kw in self._model.data.keywords:
            self._model.data.keywords.remove(kw)
            self._view.update_keywords(self._model.data.keywords)

    def on_investigator_selected(self, name: str):
        self._model.data.selected_investigator = name or None

    # --------------------------------------------------
    # INVESTIGATORS
    # --------------------------------------------------
    def load_investigators(self):
        try:
            items = self._model.load_investigators()
            self._view.populate_investigators(items)
        except Exception as e:
            self._view.show_error(f"Cannot load investigators: {e}")

    def create_investigator(
        self,
        firstname: str,
        lastname: str,
        institution: str,
        email: str,
    ):
        try:
            items = self._model.add_investigator(firstname, lastname, institution, email)
            self._view.populate_investigators(items)
        except Exception as e:
            self._view.show_error(f"Cannot create investigator: {e}")

    # --------------------------------------------------
    # SUBMIT / CANCEL
    # --------------------------------------------------
    def submit(self, e=None):
        try:
            project = self._model.create_project()
        except Exception as err:
            self._view.show_error(str(err))
            return

        # chiudo dialog
        self._view.close_dialog()

        # callback al chiamante
        if self._on_created:
            # cerco una label sensata
            proj_id = self._model.data.project_id.strip()
            label = (self._model.data.title or proj_id).strip() or proj_id
            self._on_created(proj_id, label)

    def cancel(self, e=None):
        self._view.close_dialog()
        if self._on_cancel:
            self._on_cancel()

    # --------------------------------------------------
    # VALIDAZIONE SUBMIT
    # --------------------------------------------------
    def _update_can_submit(self):
        d = self._model.data
        can = bool(d.title.strip()) and bool(d.project_id.strip())
        self._view.set_submit_enabled(can)
