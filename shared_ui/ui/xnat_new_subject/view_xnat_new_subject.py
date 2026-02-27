import flet as ft

from shared_ui.ui.base_view import BaseView


class ViewXnatNewSubject(BaseView):
    def __init__(self, page: ft.Page, on_submit=None, on_cancel=None):
        super().__init__(page)
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None

        self.dd_project = None
        self.txt_subject_name = None
        self.txt_subject_id = None
        self.chk_edit_id = None

        self.dd_gender = None
        self.txt_height_inches = None
        self.txt_weight_lbs = None
        self.txt_recruitment_source = None

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
        self.txt_subject_name.value = ""
        self.txt_subject_id.value = ""
        self.txt_subject_id.disabled = True
        self.chk_edit_id.value = False
        self.dd_gender.value = None
        self.txt_height_inches.value = ""
        self.txt_weight_lbs.value = ""
        self.txt_recruitment_source.value = ""
        self.btn_submit.disabled = True

    def set_project_options(self, projects):
        self.dd_project.options = [ft.dropdown.Option(project) for project in projects]
        self.update_page()

    def set_subject_id_value(self, value):
        self.txt_subject_id.value = value
        self._page.update()

    def set_subject_id_editable(self, editable):
        self.txt_subject_id.disabled = not editable
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

        self.txt_subject_name = ft.TextField(label="Subject name *", expand=True)

        self.txt_subject_id = ft.TextField(
            label="Subject ID *",
            disabled=True,
            expand=True,
        )
        self.chk_edit_id = ft.Checkbox(label="Edit ID")

        self.dd_gender = ft.Dropdown(
            label="Gender",
            width=320,
            options=[
                ft.dropdown.Option("male"),
                ft.dropdown.Option("female"),
                ft.dropdown.Option("unknown"),
            ],
        )

        self.txt_height_inches = ft.TextField(
            label="Height (inches)",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]*"),
        )
        self.txt_weight_lbs = ft.TextField(
            label="Weight (lbs)",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]*"),
        )
        self.txt_recruitment_source = ft.TextField(label="Recruitment Source")

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
            [self.txt_subject_id, self.chk_edit_id],
            spacing=10,
        )

        content = ft.Column(
            width=600,
            spacing=12,
            controls=[
                self.dd_project,
                self.txt_subject_name,
                id_row,
                self.dd_gender,
                self.txt_height_inches,
                self.txt_weight_lbs,
                self.txt_recruitment_source,
                self.txt_error,
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

    def _on_submit(self, e):
        if self.on_submit_callback:
            self.on_submit_callback()

        self.close()

    def _on_cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()