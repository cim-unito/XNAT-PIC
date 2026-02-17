class XnatNewSubjectData:
    def __init__(self):
        self.title = ""
        self.subject_id = ""
        self.parent_project = ""
        self.gender = ""
        self.date_of_birth = ""
        self.weight = "0"
        self.weight_unit = "g"
        self.description = ""
        self.editable_id = False
        self.error_message = ""

    def reset(self):
        self.title = ""
        self.subject_id = ""
        self.parent_project = ""
        self.gender = ""
        self.date_of_birth = ""
        self.weight = "0"
        self.weight_unit = "g"
        self.description = ""
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