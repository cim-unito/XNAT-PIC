class ControllerXnatNewProject:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view.txt_title.on_change = self.on_title_changed
        self._view.txt_project_id.on_change = self.on_project_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id

    def on_title_changed(self, e):
        d = self._model.data
        d.title = e.control.value

        if not d.editable_id:
            d.project_id = d.title.lower().replace(" ", "_")
            self._view.set_project_id_value(d.project_id)

        self._update_submit()

    def on_project_id_changed(self, e):
        self._model.data.project_id = e.control.value
        self._update_submit()

    def on_toggle_edit_id(self, e):
        d = self._model.data
        d.editable_id = e.control.value
        self._view.txt_project_id.disabled = not d.editable_id
        self._view._page.update()

    def reset_form(self):
        self._model.reset()
        self._view.reset_form()

    def _update_submit(self):
        d = self._model.data
        can = bool(d.title.strip()) and bool(d.project_id.strip())
        self._view.set_submit_enabled(can)
