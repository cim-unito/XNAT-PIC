class ControllerXnatNewSubject:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view.txt_title.on_change = self.on_title_changed
        self._view.txt_subject_id.on_change = self.on_subject_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id

    def on_title_changed(self, e):
        d = self._model.data
        d.title = e.control.value

        if not d.editable_id:
            d.subject_id = d.title.lower().replace(" ", "_")
            self._view.set_subject_id_value(d.subject_id)

        self._update_submit()

    def on_subject_id_changed(self, e):
        self._model.data.subject_id = e.control.value
        self._update_submit()

    def on_toggle_edit_id(self, e):
        d = self._model.data
        d.editable_id = e.control.value
        self._view.set_subject_id_editable(d.editable_id)

    def reset_form(self):
        self._model.reset()
        self._view.reset_form()

    def _update_submit(self):
        d = self._model.data
        can = bool(d.title.strip()) and bool(d.subject_id.strip())
        self._view.set_submit_enabled(can)
