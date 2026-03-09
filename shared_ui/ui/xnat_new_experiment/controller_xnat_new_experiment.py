class ControllerXnatNewExperiment:
    def __init__(self, view, model, on_submit=None):
        self._view = view
        self._model = model
        self._on_submit = on_submit

        self._view.txt_experiment_name.on_change = self.on_experiment_name_changed
        self._view.txt_experiment_id.on_change = self.on_experiment_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id
        self._view.on_submit_callback = self.on_submit_requested

    def on_experiment_name_changed(self, e):
        experiment_name = e.control.value

        if not self._view.chk_edit_id.value:
            experiment_id = self._model.generate_experiment_id(experiment_name)
            self._view.set_experiment_id_value(experiment_id)

        self._update_submit()

    def on_experiment_id_changed(self, e):
        self._update_submit()

    def on_toggle_edit_id(self, e):
        editable = e.control.value
        self._view.set_experiment_id_editable(editable)

        if not editable:
            experiment_name = self._view.txt_experiment_name.value
            self._view.set_experiment_id_value(self._model.generate_experiment_id(experiment_name))

        self._update_submit()

    def on_submit_requested(self):
        payload = self._model.build_payload(
            self._view.dd_project.value,
            self._view.dd_subject.value,
            self._view.txt_experiment_name.value,
            self._view.txt_experiment_id.value,
        )

        if self._on_submit:
            self._on_submit(payload)

    def reset_form(self):
        self._view.reset_form()

    def _update_submit(self):
        self._view.set_submit_enabled(
            self._model.can_submit(
                self._view.dd_project.value,
                self._view.dd_subject.value,
                self._view.txt_experiment_name.value,
                self._view.txt_experiment_id.value,
            )
        )
