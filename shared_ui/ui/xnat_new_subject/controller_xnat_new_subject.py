from datetime import datetime
import re


class ControllerXnatNewSubject:
    ID_ALLOWED_PATTERN = re.compile(r"[^a-zA-Z0-9_]")

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view.txt_title.on_change = self.on_title_changed
        self._view.txt_subject_id.on_change = self.on_subject_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id
        self._view.dd_project.on_change = self.on_project_changed
        self._view.rg_yob_dob_age.on_change = self.on_yob_dob_age_mode_changed
        self._view.dd_gender.on_change = self.on_gender_changed
        self._view.txt_date_of_birth.on_change = self.on_date_of_birth_changed
        self._view.txt_year_of_birth.on_change = self.on_year_of_birth_changed
        self._view.txt_age.on_change = self.on_age_changed
        self._view.dd_handedness.on_change = self.on_handedness_changed
        self._view.txt_education.on_change = self.on_education_changed
        self._view.txt_race.on_change = self.on_race_changed
        self._view.txt_ethnicity.on_change = self.on_ethnicity_changed
        self._view.txt_height_inches.on_change = self.on_height_inches_changed
        self._view.txt_weight_lbs.on_change = self.on_weight_lbs_changed
        self._view.txt_recruitment_source.on_change = self.on_recruitment_source_changed

    def configure_context(self, projects, existing_subject_ids_by_project=None):
        self._model.set_projects_context(projects, existing_subject_ids_by_project)
        self._view.set_project_options(self._model.available_projects)
        self._update_submit()

    def on_title_changed(self, e):
        d = self._model.data
        d.title = (e.control.value or "").strip()

        if not d.editable_id:
            d.subject_id = self._build_subject_id_from_title(d.title)
            self._view.set_subject_id_value(d.subject_id)

        self._update_submit()

    def on_subject_id_changed(self, e):
        d = self._model.data
        raw_subject_id = (e.control.value or "").strip()

        if d.editable_id:
            sanitized_subject_id = self._sanitize_subject_id(raw_subject_id)
            if sanitized_subject_id != raw_subject_id:
                self._view.set_subject_id_value(sanitized_subject_id)
            d.subject_id = sanitized_subject_id
        else:
            d.subject_id = self._build_subject_id_from_title(d.title)
            self._view.set_subject_id_value(d.subject_id)

        self._update_submit()

    def on_project_changed(self, e):
        self._model.data.parent_project = (e.control.value or "").strip()

        self._view.set_subject_id_editable(self._model.data.editable_id)

        self._update_submit()

    def on_yob_dob_age_mode_changed(self, e):
        mode = e.control.value
        self._model.data.yob_dob_age_mode = mode
        self._view.set_yob_dob_age_mode(mode)
        self._update_submit()

    def on_gender_changed(self, e):
        self._model.data.gender = (e.control.value or "").strip()

    def on_date_of_birth_changed(self, e):
        formatted_value = self._format_date_of_birth_input(e.control.value or "")
        if formatted_value != (e.control.value or ""):
            self._view.set_date_of_birth_value(formatted_value)

        self.set_date_of_birth_value(formatted_value)

    def set_date_of_birth_value(self, raw_value):
        d = self._model.data
        date_txt = (raw_value or "").strip()
        if not date_txt:
            d.date_of_birth = ""
            self._update_submit()
            return

        try:
            selected = datetime.strptime(date_txt, "%m/%d/%Y")
            now = datetime.now()
            d.date_of_birth = date_txt if selected <= now else now.strftime("%m/%d/%Y")
            self._view.set_date_of_birth_value(d.date_of_birth)
        except ValueError:
            d.date_of_birth = ""

        self._update_submit()

    def _format_date_of_birth_input(self, raw_value):
        digits = "".join(ch for ch in (raw_value or "") if ch.isdigit())[:8]

        if len(digits) <= 2:
            return digits
        if len(digits) <= 4:
            return f"{digits[:2]}/{digits[2:]}"

        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"

    def on_year_of_birth_changed(self, e):
        sanitized = self._numeric_prefix(e.control.value, max_len=4)
        if sanitized != (e.control.value or ""):
            self._view.txt_year_of_birth.value = sanitized
            self._view.update_page()
        self._model.data.year_of_birth = sanitized
        self._update_submit()

    def on_age_changed(self, e):
        sanitized = self._numeric_prefix(e.control.value, max_len=3)
        if sanitized != (e.control.value or ""):
            self._view.txt_age.value = sanitized
            self._view.update_page()
        self._model.data.age = sanitized
        self._update_submit()

    def on_handedness_changed(self, e):
        self._model.data.handedness = (e.control.value or "").strip()

    def on_education_changed(self, e):
        self._model.data.education = (e.control.value or "").strip()

    def on_race_changed(self, e):
        self._model.data.race = (e.control.value or "").strip()

    def on_ethnicity_changed(self, e):
        self._model.data.ethnicity = (e.control.value or "").strip()

    def on_height_inches_changed(self, e):
        self._model.data.height_inches = (e.control.value or "").strip()
        self._update_submit()

    def on_weight_lbs_changed(self, e):
        self._model.data.weight_lbs = (e.control.value or "").strip()
        self._update_submit()

    def on_recruitment_source_changed(self, e):
        self._model.data.recruitment_source = (e.control.value or "").strip()

    def on_toggle_edit_id(self, e):
        d = self._model.data
        d.editable_id = bool(e.control.value)

        if not d.editable_id:
            d.subject_id = self._build_subject_id_from_title(d.title)
            self._view.set_subject_id_value(d.subject_id)

        self._view.set_subject_id_editable(d.editable_id)
        self._update_submit()

    def reset_form(self):
        self._model.reset()
        self._view.reset_form()
        self.set_date_of_birth_value(self._view.txt_date_of_birth.value)
        self._update_submit()

    def _build_subject_id_from_title(self, title):
        return self._sanitize_subject_id((title or "").strip().lower())

    def _sanitize_subject_id(self, value):
        value = (value or "").strip().replace(" ", "_")
        value = self.ID_ALLOWED_PATTERN.sub("_", value)

        while "__" in value:
            value = value.replace("__", "_")

        return value.strip("_")

    def _numeric_prefix(self, raw_value, max_len):
        return "".join(ch for ch in (raw_value or "") if ch.isdigit())[:max_len]

    def _validate_numeric_float(self, value, field_name):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return None

        try:
            parsed_value = float(normalized_value)
        except ValueError:
            return f"{field_name} must be numeric."

        if parsed_value < 0:
            return f"{field_name} must be a non-negative number."

        return None

    def _update_submit(self):
        d = self._model.data
        d.error_message = ""

        can = all([
            bool(d.parent_project.strip()),
            bool(d.title.strip()),
            bool(d.subject_id.strip()),
        ])

        if can:
            current_mode = d.yob_dob_age_mode
            if current_mode == "dob":
                if not d.date_of_birth:
                    d.error_message = "Date of birth must be a valid date in MM/DD/YYYY format."
                    can = False
            elif current_mode == "yob":
                year = d.year_of_birth.strip()
                now_year = datetime.now().year
                if not year.isdigit() or len(year) != 4 or not (1900 <= int(year) <= now_year):
                    d.error_message = "Year of birth must be a 4-digit year between 1900 and current year."
                    can = False
            elif current_mode == "age":
                age = d.age.strip()
                if not age.isdigit() or not (0 <= int(age) <= 130):
                    d.error_message = "Age must be a number between 0 and 130."
                    can = False

        if can:
            d.error_message = self._validate_numeric_float(d.height_inches, "Height") or ""
            can = not d.error_message

        if can:
            d.error_message = self._validate_numeric_float(d.weight_lbs, "Weight") or ""
            can = not d.error_message

        if can:
            existing = self._model.existing_subject_ids_by_project.get(d.parent_project, set())
            if d.subject_id in existing:
                d.error_message = (
                    f"A Subject with the same subject_id already exists in project '{d.parent_project}'."
                )
                can = False

        self._view.set_error_message(d.error_message)
        self._view.set_submit_enabled(can)
