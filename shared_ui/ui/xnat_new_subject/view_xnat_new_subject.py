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
        self.rg_yob_dob_age = None
        self.txt_date_of_birth = None
        self.txt_year_of_birth = None
        self.txt_age = None
        self.dd_gender = None
        self.dd_handedness = None
        self.txt_education = None
        self.txt_race = None
        self.txt_ethnicity = None
        self.txt_height_inches = None
        self.txt_weight_lbs = None
        self.txt_recruitment_source = None
        self.txt_error = None
        self.btn_submit = None
        self.btn_cancel = None
        self.id_row = None
        self.row_dob = None
        self.row_yob = None
        self.row_age = None

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
            spacing=10,
        )

        self.rg_yob_dob_age = ft.RadioGroup(
            value="dob",
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        [
                            ft.Radio(value="dob", label="Date Of Birth"),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Radio(value="yob", label="Year Of Birth"),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Radio(value="age", label="Age"),
                        ]
                    ),
                ],
            ),
        )

        self.txt_date_of_birth = ft.TextField(
            label="Date of birth",
            hint_text="MM/DD/YYYY",
            width=180,
            keyboard_type=ft.KeyboardType.DATETIME,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"),
            max_length=10,
        )
        self.row_dob = ft.Row([self.txt_date_of_birth], spacing=8)

        self.txt_year_of_birth = ft.TextField(
            label="YYYY",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"),
            max_length=4,
        )
        self.row_yob = ft.Row([self.txt_year_of_birth], visible=False)

        self.txt_age = ft.TextField(
            label="Age",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"),
            max_length=4,
        )

        self.row_age = ft.Row([self.txt_age], visible=False)

        self.dd_gender = ft.Dropdown(
            label="Gender",
            width=320,
            options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Unknown"),
            ],
        )

        self.dd_handedness = ft.Dropdown(
            label="Handedness",
            width=320,
            options=[
                ft.dropdown.Option("Right"),
                ft.dropdown.Option("Left"),
                ft.dropdown.Option("Ambidextrous"),
                ft.dropdown.Option("Unknown"),
            ],
        )

        self.txt_education = ft.TextField(label="Education")
        self.txt_race = ft.TextField(label="Race")
        self.txt_ethnicity = ft.TextField(label="Ethnicity")
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
        self.txt_date_of_birth.on_blur = self._on_date_text_blur

    def _define_layout(self):
        yob_dob_age_box = ft.Container(
            border=ft.border.all(1, ft.Colors.BLACK26),
            padding=12,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Please Select One"),
                    ft.Row(
                        [
                            ft.Container(width=180, content=self.rg_yob_dob_age),
                            ft.Column(
                                spacing=8,
                                controls=[
                                    self.row_dob,
                                    self.row_yob,
                                    self.row_age,
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
            ),
        )

        content = ft.Column(
            width=600,
            spacing=12,
            controls=[
                self.dd_project,
                self.txt_title,
                self.id_row,
                yob_dob_age_box,
                self.dd_gender,
                self.dd_handedness,
                self.txt_education,
                self.txt_race,
                self.txt_ethnicity,
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

    def set_initial_state(self):
        self.txt_title.value = ""
        self.dd_project.value = None
        self.txt_subject_id.value = ""
        self.txt_subject_id.disabled = True
        self.chk_edit_id.value = False
        self.rg_yob_dob_age.value = "dob"
        self.txt_date_of_birth.value = datetime.now().strftime("%m/%d/%Y")
        self.txt_year_of_birth.value = ""
        self.txt_age.value = ""
        self._apply_yob_dob_age_visibility("dob")
        self.dd_gender.value = None
        self.dd_handedness.value = None
        self.txt_education.value = ""
        self.txt_race.value = ""
        self.txt_ethnicity.value = ""
        self.txt_height_inches.value = ""
        self.txt_weight_lbs.value = ""
        self.txt_recruitment_source.value = ""
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

    def set_yob_dob_age_mode(self, mode):
        self.rg_yob_dob_age.value = mode
        self._apply_yob_dob_age_visibility(mode)
        self.update_page()

    def _apply_yob_dob_age_visibility(self, mode):
        self.row_dob.visible = mode == "dob"
        self.row_yob.visible = mode == "yob"
        self.row_age.visible = mode == "age"

    def set_controller(self, controller):
        self._controller = controller

    def _on_date_text_blur(self, e):
        if getattr(self, "_controller", None):
            self._controller.set_date_of_birth_value(self.txt_date_of_birth.value)

    def _on_submit(self, e):
        title_value = (self.txt_title.value or "").strip()

        data = {
            "parent_project": (self.dd_project.value or "").strip(),
            "title": title_value,
            "subject_name": title_value,
            "subject_id": (self.txt_subject_id.value or "").strip(),
            "yob_dob_age_mode": self.rg_yob_dob_age.value,
            "date_of_birth": (self.txt_date_of_birth.value or "").strip(),
            "year_of_birth": (self.txt_year_of_birth.value or "").strip(),
            "age": (self.txt_age.value or "").strip(),
            "gender": (self.dd_gender.value or "").strip(),
            "handedness": (self.dd_handedness.value or "").strip(),
            "education": (self.txt_education.value or "").strip(),
            "race": (self.txt_race.value or "").strip(),
            "ethnicity": (self.txt_ethnicity.value or "").strip(),
            "height_inches": (self.txt_height_inches.value or "").strip(),
            "weight_lbs": (self.txt_weight_lbs.value or "").strip(),
            "recruitment_source": (self.txt_recruitment_source.value or "").strip(),
        }

        if self.on_submit_callback:
            self.on_submit_callback(data)

        self.close()

    def _on_cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()