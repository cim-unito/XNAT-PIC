from datetime import datetime
import re


class ControllerXnatNewSubject:
    def __init__(self, view, model, on_submit=None):
        self._view = view
        self._model = model
        self._on_submit = on_submit

        self._view.txt_subject_name.on_change = self.on_subject_name_changed
        self._view.txt_subject_id.on_change = self.on_subject_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id
        self._view.on_submit_callback = self.on_submit_requested

    def on_subject_name_changed(self, e):
        subject_name = e.control.value

        if not self._view.chk_edit_id.value:
            subject_id = self._model.generate_subject_id(subject_name)
            self._view.set_subject_id_value(subject_id)

        self._update_submit()

    def on_subject_id_changed(self, e):
        self._update_submit()

    def on_toggle_edit_id(self, e):
        editable = e.control.value
        self._view.set_subject_id_editable(editable)

        if not editable:
            subject_name = self._view.txt_subject_name.value
            self._view.set_subject_id_value(self._model.generate_subject_id(subject_name))

        self._update_submit()

    def on_submit_requested(self):
        selected_mode = self._view.rg_yob_dob_age.value
        date_of_birth = ""
        year_of_birth = ""
        age = ""

        if selected_mode == "dob":
            date_of_birth = (self._view.txt_date_of_birth.value or "").strip()
        elif selected_mode == "yob":
            year_of_birth = (self._view.txt_year_of_birth.value or "").strip()
        elif selected_mode == "age":
            age = (self._view.txt_age.value or "").strip()

        payload = self._model.build_payload(
            self._view.dd_project.value,
            self._view.txt_project_name.value,
            self._view.txt_project_id.value,
            selected_mode,
            date_of_birth,
            year_of_birth,
            age,
            self._view.dd_gender.value,
            self._view.txt_height_inches.value,
            self._view.txt_weight_lbs.value,
            self._view.txt_recruitment_source.value
        )

        if self._on_submit:
            self._on_submit(payload)

    def reset_form(self):
        self._view.reset_form()

    def _update_submit(self):
        self._view.set_submit_enabled(
            self._model.can_submit(
                self._view.dd_project.value,
                self._view.txt_subject_name.value,
                self._view.txt_subject_id.value,
            )
        )
