import flet as ft

from shared_ui.ui.shared_view.base_view import BaseView


class ViewXnatNewExperiment(BaseView):
    def __init__(self, page: ft.Page, on_submit=None, on_cancel=None):
        super().__init__(page)
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None

        self.dd_project = None
        self.dd_subject = None
        self.txt_experiment_label = None

        self.btn_submit = None
        self.btn_cancel = None

        self.build_dialog()

    def build_dialog(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self.dlg

    def set_initial_state(self):
        self.dd_project.value = None
        self.dd_subject.value = None
        self.txt_experiment_label.value = ""
        self.btn_submit.disabled = True

    def populate_project_options(self, projects: list[dict[str, str]]):
        self.dd_project.options = [
            ft.dropdown.Option(key=p["id"], text=p["name"]) for p in projects
        ]
        self.dd_project.value = None

        self.update_page()

    def populate_subject_options(self, subjects: list[dict[str, str]]):
        self.dd_subject.options = [
            ft.dropdown.Option(key=s["id"], text=s["label"]) for s in subjects
        ]
        self.dd_subject.value = None

        self._page.update()

    def set_subject_options(self, subject_ids_names: list[tuple[str, str]]):
        self.dd_subject.options = [
            ft.dropdown.Option(
                key=str(subject_id),
                text=subject_name
            )
            for subject_id, subject_name in subject_ids_names
        ]
        self.update_page()

    def set_submit_enabled(self, enabled: bool):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def reset_form(self):
        self.dd_project.options = []
        self.dd_subject.options = []
        self.set_initial_state()
        self._page.update()

    def reset_form_subject(self):
        self.dd_subject.options = []
        self.dd_subject.key = "Select"
        self.dd_subject.value = None
        self.txt_experiment_label.value = ""
        self.btn_submit.disabled = True
        self._page.update()

    def open(self):
        if not self.dlg:
            self.build_dialog()

        self._page.open(self.dlg)
        self._page.update()

    def close(self):
        self._page.close(self.dlg)
        self._page.update()

    def _build_controls(self):
        self.dd_project = ft.Dropdown(label="Parent project *", options=[], expand=True)

        self.dd_subject = ft.Dropdown(label="Parent subject *", options=[], expand=True)

        self.txt_experiment_label = ft.TextField(label="Experiment name *", expand=True)

        self.btn_cancel = ft.TextButton("Close")
        self.btn_submit = ft.ElevatedButton(
            "Submit",
            disabled=True,
        )

    def _bind_events(self):
        self.btn_cancel.on_click = self._on_cancel
        self.btn_submit.on_click = self._on_submit

    def _define_layout(self):
        content = ft.Column(
            width=600,
            spacing=12,
            controls=[
                self.dd_project,
                self.dd_subject,
                self.txt_experiment_label,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("New XNAT experiment"),
            content=content,
            actions=[self.btn_cancel, self.btn_submit],
            content_padding=ft.Padding(20, 12, 20, 16),
            actions_padding=ft.Padding(12, 0, 12, 12),
        )

    def _on_submit(self, e: ft.ControlEvent):
        if self.on_submit_callback:
            self.on_submit_callback()

        self.close()

    def _on_cancel(self, e: ft.ControlEvent):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()