import flet as ft

from shared_ui.ui.base_view import BaseView


class ViewXnatNewExperiment(BaseView):
    def __init__(self, page: ft.Page, on_submit=None, on_cancel=None):
        super().__init__(page)
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None

        self.dd_project = None
        self.dd_subject = None
        self.txt_experiment_name = None
        self.txt_experiment_id = None
        self.chk_edit_id = None

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
        self.txt_experiment_name.value = ""
        self.txt_experiment_id.value = ""
        self.txt_experiment_id.disabled = True
        self.chk_edit_id.value = False
        self.btn_submit.disabled = True

    def set_project_options(self, projects):
        self.dd_project.options = [ft.dropdown.Option(project) for project in projects]
        self.update_page()

    def set_subject_options(self, subjects):
        self.dd_subject.options = []

        for subject in subjects:
            if isinstance(subject, dict):
                self.dd_subject.options.append(
                    ft.dropdown.Option(
                        key=subject.get("id"),
                        text=subject.get("label") or subject.get("id"),
                    )
                )
            else:
                self.dd_subject.options.append(ft.dropdown.Option(subject))

    def set_experiment_id_value(self, value):
        self.txt_experiment_id.value = value
        self._page.update()

    def set_experiment_id_editable(self, editable):
        self.txt_experiment_id.disabled = not editable
        self.update_page()

    def set_submit_enabled(self, enabled):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def reset_form(self):
        self.set_initial_state()
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

        self.txt_experiment_name = ft.TextField(label="Experiment name *", expand=True)

        self.txt_experiment_id = ft.TextField(
            label="Experiment ID *",
            disabled=True,
            expand=True,
        )
        self.chk_edit_id = ft.Checkbox(label="Edit ID")

        self.txt_error = ft.Text(value="", color=ft.Colors.RED_600)

        self.btn_cancel = ft.TextButton("Close")
        self.btn_submit = ft.ElevatedButton(
            "Submit",
            disabled=True,
        )

    def _bind_events(self):
        self.btn_cancel.on_click = self._on_cancel
        self.btn_submit.on_click = self._on_submit

    def _define_layout(self):
        id_row = ft.Row(
            [self.txt_experiment_id, self.chk_edit_id],
            spacing=10,
        )

        content = ft.Column(
            width=600,
            spacing=12,
            controls=[
                self.dd_project,
                self.dd_subject,
                self.txt_experiment_name,
                id_row,
                self.txt_error,
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

    def _on_submit(self, e):
        if self.on_submit_callback:
            self.on_submit_callback()

        self.close()

    def _on_cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()