import flet as ft
from datetime import datetime

from shared_ui.ui.base_view import BaseView

class ViewXnatNewSubject(BaseView):
    def __init__(self, page: ft.Page, on_submit, on_cancel=None):
        super().__init__(page)
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None
        self.txt_title = None
        self.dd_project = None
        self.txt_subject_id = None
        self.chk_edit_id = None
        self.dd_gender = None
        self.txt_date_of_birth = None
        self.txt_weight = None
        self.dd_weight_unit = None
        self.txt_description = None
        self.txt_error = None
        self.btn_submit = None
        self.btn_cancel = None
        self.id_row = None

        self.build_dialog()

    def build_dialog(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self.dlg

    def _build_controls(self):
        self.dd_project = ft.Dropdown(label="Parent project *", options=[], width=600)

        self.txt_title = ft.TextField(label="Subject title *", width=600)

        self.txt_subject_id = ft.TextField(
            label="Subject ID *",
            disabled=True,
            expand=True,
        )

        self.chk_edit_id = ft.Checkbox(label="Edit ID")

        self.id_row = ft.Row(
            [self.txt_subject_id, self.chk_edit_id],
            spacing=10
        )

        self.dd_gender = ft.Dropdown(
            label="Gender",
            options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Other"),
            ],
        )

        self.txt_date_of_birth = ft.TextField(label="Date of birth (MM/DD/YYYY)")

        self.txt_weight = ft.TextField(label="Weight", width=240)
        self.dd_weight_unit = ft.Dropdown(
            label="Unit",
            value="g",
            width=120,
            options=[
                ft.dropdown.Option("g"),
                ft.dropdown.Option("lbs"),
            ],
        )

        self.txt_description = ft.TextField(
            label="Subject description",
            multiline=True,
            min_lines=1,
            max_lines=6
        )

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

        content = ft.Column(
            width=600,
            spacing=16,
            controls=[
                self.dd_project,
                self.txt_title,
                self.id_row,
                self.dd_gender,
                self.txt_date_of_birth,
                ft.Row([self.txt_weight, self.dd_weight_unit], spacing=10),
                self.txt_description,
                self.txt_error,
            ]
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("New XNAT subject"),
            content=content,
            actions=[self.btn_cancel, self.btn_submit],
            content_padding=ft.Padding(20, 12, 20, 16),
            actions_padding=ft.Padding(12, 0, 12, 12),
        )

    def set_initial_state(self):
        self.txt_title.value = ""
        self.dd_project.value = None
        self.txt_subject_id.value = ""
        self.txt_subject_id.disabled = True
        self.chk_edit_id.value = False
        self.dd_gender.value = None
        self.txt_date_of_birth.value = datetime.now().strftime("%m/%d/%Y")
        self.txt_weight.value = "0"
        self.dd_weight_unit.value = "g"
        self.txt_description.value = ""
        self.txt_error.value = ""
        self.btn_submit.disabled = True

    def open(self):
        if not self.dlg:
            self.build_dialog()

        self._page.open(self.dlg)
        self._page.update()

    def reset_form(self):
        self.set_initial_state()
        self._page.update()

    def close(self):
        self._page.close(self.dlg)
        self._page.update()

    def close_dialog(self):
        self.close()

    def set_subject_id_value(self, value):
        self.txt_subject_id.value = value
        self._page.update()

    def set_submit_enabled(self, enabled):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def set_project_options(self, projects):
        self.dd_project.options = [ft.dropdown.Option(project) for project in projects]
        self.update_page()

    def set_error_message(self, message):
        self.txt_error.value = message or ""
        self.update_page()

    def set_date_of_birth_value(self, value):
        self.txt_date_of_birth.value = value
        self.update_page()

    def set_subject_id_editable(self, editable):
        self.txt_subject_id.disabled = not editable
        self.update_page()

    def set_controller(self, controller):
        self._controller = controller

    def _on_submit(self, e):
        data = {
            "parent_project": self.dd_project.value,
            "subject_name": self.txt_title.value,
            "subject_id": self.txt_subject_id.value,
            "gender": self.dd_gender.value,
            "date_of_birth": self.txt_date_of_birth.value,
            "weight": self.txt_weight.value,
            "weight_unit": self.dd_weight_unit.value,
            "description": self.txt_description.value,
            "notes": self.txt_description.value,
        }

        if self.on_submit_callback:
            self.on_submit_callback(data)

        self.close()

    def _on_cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()
