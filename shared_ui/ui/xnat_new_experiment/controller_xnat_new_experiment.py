import flet as ft

class ControllerXnatNewExperiment:
    def __init__(self, view, model, on_submit=None):
        self._view = view
        self._model = model
        self._on_submit = on_submit

        self._view.dd_project.on_change = self.on_project_changed
        self._view.dd_subject.on_change = self.on_subject_changed
        self._view.txt_experiment_label.on_change = self.on_experiment_label_changed
        self._view.on_submit_callback = self.on_submit_requested

    def on_project_changed(self, e: ft.ControlEvent):
        self.update_submit()

    def on_subject_changed(self, e: ft.ControlEvent):
        self.update_submit()

    def on_experiment_label_changed(self, e: ft.ControlEvent):
        self.update_submit()

    def on_submit_requested(self):
        payload = self._model.build_payload(
            self._view.dd_project.value,
            self._view.dd_subject.value,
            self._view.txt_experiment_label.value,
        )

        if self._on_submit:
            self._on_submit(payload)

    def reset_form(self):
        self._view.reset_form()

    def update_submit(self):
        self._view.set_submit_enabled(
            self._model.can_submit(
                self._view.dd_project.value,
                self._view.dd_subject.value,
                self._view.txt_experiment_label.value,
            )
        )
