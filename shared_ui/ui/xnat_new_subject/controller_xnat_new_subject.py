from datetime import datetime


class ControllerXnatNewSubject:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view.txt_title.on_change = self.on_title_changed
        self._view.txt_subject_id.on_change = self.on_subject_id_changed
        self._view.chk_edit_id.on_change = self.on_toggle_edit_id
        self._view.dd_project.on_change = self.on_project_changed
        self._view.dd_gender.on_change = self.on_gender_changed
        self._view.txt_date_of_birth.on_change = self.on_date_of_birth_changed
        self._view.txt_weight.on_change = self.on_weight_changed
        self._view.dd_weight_unit.on_change = self.on_weight_unit_changed
        self._view.txt_description.on_change = self.on_description_changed

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

    def on_gender_changed(self, e):
        self._model.data.gender = e.control.value or ""

    def on_date_of_birth_changed(self, e):
        date_txt = (e.control.value or "").strip()
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

    def on_weight_changed(self, e):
        self._model.data.weight = (e.control.value or "").strip()

    def on_weight_unit_changed(self, e):
        self._model.data.weight_unit = e.control.value or "g"

    def on_description_changed(self, e):
        self._model.data.description = e.control.value or ""

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

        existing = self._model.existing_subject_ids_by_project.get(d.parent_project, set())
        if d.subject_id and d.subject_id in existing:
            d.error_message = (
                f"A Subject with the same subject_id already exists in project '{d.parent_project}'."
            )
            can = False

        self._view.set_error_message(d.error_message)
        self._view.set_submit_enabled(can)