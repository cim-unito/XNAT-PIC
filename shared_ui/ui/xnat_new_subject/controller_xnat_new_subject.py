from datetime import datetime


class ControllerXnatNewSubject:
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
        d.title = e.control.value

        if not d.editable_id:
            d.subject_id = d.title.lower().replace(" ", "_")
            self._view.set_subject_id_value(d.subject_id)

        self._update_submit()

    def on_subject_id_changed(self, e):
        self._model.data.subject_id = e.control.value
        self._update_submit()

    def on_project_changed(self, e):
        self._model.data.parent_project = e.control.value or ""

        self._view.set_subject_id_editable(self._model.data.editable_id)

        self._update_submit()

    def on_yob_dob_age_mode_changed(self, e):
        mode = e.control.value or "dob"
        self._model.data.yob_dob_age_mode = mode
        self._view.set_yob_dob_age_mode(mode)
        self._update_submit()

    def on_gender_changed(self, e):
        self._model.data.gender = e.control.value or ""

    def on_date_of_birth_changed(self, e):
        self.set_date_of_birth_value(e.control.value or "")

    def set_date_of_birth_value(self, raw_value):
        date_txt = (raw_value or "").strip()
        if not date_txt:
            self._model.data.date_of_birth = ""
            self._update_submit()
            return

        try:
            selected = datetime.strptime(date_txt, "%m/%d/%Y")
            now = datetime.now()
            self._model.data.date_of_birth = date_txt if selected <= now else now.strftime("%m/%d/%Y")
            self._view.set_date_of_birth_value(self._model.data.date_of_birth)
        except ValueError:
            self._model.data.date_of_birth = ""

        self._update_submit()

    def on_year_of_birth_changed(self, e):
        self._model.data.year_of_birth = (e.control.value or "").strip()
        self._update_submit()

    def on_age_changed(self, e):
        self._model.data.age = (e.control.value or "").strip()
        self._update_submit()

    def on_handedness_changed(self, e):
        self._model.data.handedness = e.control.value or ""

    def on_education_changed(self, e):
        self._model.data.education = (e.control.value or "").strip()

    def on_race_changed(self, e):
        self._model.data.race = (e.control.value or "").strip()

    def on_ethnicity_changed(self, e):
        self._model.data.ethnicity = (e.control.value or "").strip()

    def on_height_inches_changed(self, e):
        self._model.data.height_inches = (e.control.value or "").strip()

    def on_weight_lbs_changed(self, e):
        self._model.data.weight_lbs = (e.control.value or "").strip()

    def on_recruitment_source_changed(self, e):
        self._model.data.recruitment_source = (e.control.value or "").strip()

    def on_toggle_edit_id(self, e):
        d = self._model.data
        d.editable_id = e.control.value

        if not d.editable_id:
            d.subject_id = d.title.lower().replace(" ", "_")
            self._view.set_subject_id_value(d.subject_id)

        self._view.set_subject_id_editable(d.editable_id)
        self._update_submit()

    def reset_form(self):
        self._model.reset()
        self._view.reset_form()

    def _update_submit(self):
        d = self._model.data
        d.error_message = ""

        can = bool(d.parent_project.strip()) and bool(d.title.strip()) and bool(d.subject_id.strip())

        if d.yob_dob_age_mode == "dob":
            if not d.date_of_birth:
                d.error_message = "Date of birth must be a valid date in MM/DD/YYYY format."
                can = False
        elif d.yob_dob_age_mode == "yob":
            year = d.year_of_birth.strip()
            now_year = datetime.now().year
            if not year.isdigit() or len(year) != 4 or not (1900 <= int(year) <= now_year):
                d.error_message = "Year of birth must be a 4-digit year between 1900 and current year."
                can = False
        elif d.yob_dob_age_mode == "age":
            age = d.age.strip()
            if not age.isdigit() or not (0 <= int(age) <= 130):
                d.error_message = "Age must be a number between 0 and 130."
                can = False

        if can and d.height_inches.strip():
            try:
                if float(d.height_inches) < 0:
                    d.error_message = "Height must be a positive number."
                    can = False
            except ValueError:
                d.error_message = "Height must be numeric."
                can = False

        if can and d.weight_lbs.strip():
            try:
                if float(d.weight_lbs) < 0:
                    d.error_message = "Weight must be a positive number."
                    can = False
            except ValueError:
                d.error_message = "Weight must be numeric."
                can = False

        existing = self._model.existing_subject_ids_by_project.get(d.parent_project, set())
        if d.subject_id and d.subject_id in existing:
            d.error_message = (
                f"A Subject with the same subject_id already exists in project '{d.parent_project}'."
            )
            can = False

        self._view.set_error_message(d.error_message)
        self._view.set_submit_enabled(can)