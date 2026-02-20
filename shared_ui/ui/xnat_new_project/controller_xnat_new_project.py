class ControllerXnatNewProject:
    def __init__(self, view, model, on_submit=None):
        self._view = view
        self._model = model
        self._on_submit = on_submit

        self._view.txt_project_name.on_change = self.on_project_name_changed
        self._view.txt_project_id.on_change = self.on_project_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id
        self._view.on_submit_callback = self.on_submit_requested

    def on_project_name_changed(self, e):
        project_name = e.control.value

        if not self._view.chk_edit_id.value:
            project_id = self._model.generate_project_id(project_name)
            self._view.set_project_id_value(project_id)

        self._update_submit()

    def on_project_id_changed(self, e):
        self._update_submit()

    def on_toggle_edit_id(self, e):
        editable = e.control.value
        self._view.set_project_id_editable(editable)

        if not editable:
            project_name = self._view.txt_project_name.value
            self._view.set_project_id_value(self._model.generate_project_id(project_name))

        self._update_submit()

    def on_submit_requested(self):
        payload = self._model.build_payload(
            self._view.txt_project_name.value,
            self._view.txt_project_id.value,
            self._view.rb_access.value,
            self._view.txt_description.value,
        )

        if self._on_submit:
            self._on_submit(payload)

    def reset_form(self):
        self._view.reset_form()

    def _update_submit(self):
        self._view.set_submit_enabled(
            self._model.can_submit(
                self._view.txt_project_name.value,
                self._view.txt_project_id.value,
            )
        )
