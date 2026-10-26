import flet as ft

from shared_ui.ui.shared_view.base_view import BaseView


class ViewXnatNewSubject(BaseView):
    def __init__(self, page: ft.Page, on_submit=None, on_cancel=None):
        super().__init__(page)
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None

        self.dd_project = None
        self.txt_subject_label = None

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
        self.txt_subject_label.value = ""
        self.btn_submit.disabled = True

    def set_project_options(self, project_ids_names: list):
        self.dd_project.options = [
            ft.dropdown.Option(
                key=str(project_id),
                text=project_name
            )
            for project_id, project_name in project_ids_names
        ]
        self.update_page()

    def set_submit_enabled(self, enabled: bool):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def reset_form(self):
        self.dd_project.options = []
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

        self.txt_subject_label = ft.TextField(label="Subject name *", expand=True)

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
                self.txt_subject_label,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("New XNAT subject"),
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