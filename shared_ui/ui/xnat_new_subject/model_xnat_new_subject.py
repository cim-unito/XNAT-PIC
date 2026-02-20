class XnatNewSubjectData:
    DEFAULT_YOB_DOB_AGE_MODE = None
    def __init__(self):
        self.title = ""
        self.subject_id = ""
        self.parent_project = ""
        self.yob_dob_age_mode = self.DEFAULT_YOB_DOB_AGE_MODE
        self.gender = ""
        self.date_of_birth = ""
        self.year_of_birth = ""
        self.age = ""
        self.height_inches = ""
        self.weight_lbs = ""
        self.recruitment_source = ""
        self.editable_id = False
        self.error_message = ""

    def reset(self):
        self.title = ""
        self.subject_id = ""
        self.parent_project = ""
        self.yob_dob_age_mode = self.DEFAULT_YOB_DOB_AGE_MODE
        self.gender = ""
        self.date_of_birth = ""
        self.year_of_birth = ""
        self.age = ""
        self.height_inches = ""
        self.weight_lbs = ""
        self.recruitment_source = ""
        self.editable_id = False
        self.error_message = ""

class ModelXnatNewSubject:
    def __init__(self):
        self.data = XnatNewSubjectData()
        self.available_projects = []
        self.existing_subject_ids_by_project = {}

    def reset(self):
        self.data.reset()

    def set_projects_context(self, projects, existing_subject_ids_by_project=None):
        self.available_projects = projects or []
        self.existing_subject_ids_by_project = existing_subject_ids_by_project or {}