from datetime import datetime
import re


class ControllerXnatNewSubject:
    ID_ALLOWED_PATTERN = re.compile(r"[^a-zA-Z0-9_]")

    def __init__(self, view, model):
        self._view = view
        self._model = model


    def on_toggle_edit_id(self, e):
        d = self._model.data
        d.editable_id = bool(e.control.value)

        if not d.editable_id:
            d.subject_id = self._build_subject_id_from_title(d.title)
            self._view.set_subject_id_value(d.subject_id)

        self._view.set_subject_id_editable(d.editable_id)
        self._update_submit()

    def reset_form(self):
        self._model.reset()
        self._view.reset_form()
        self._update_submit()

    def _update_submit(self):
        d = self._model.data
        d.error_message = ""

        can = all([
            bool(d.parent_project.strip()),
            bool(d.title.strip()),
            bool(d.subject_id.strip()),
        ])

        self._view.set_error_message(d.error_message)
        self._view.set_submit_enabled(can)
