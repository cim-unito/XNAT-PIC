class XnatNewProjectData:
    def __init__(self):
        self.title = ""
        self.project_id = ""
        self.accessibility = "private"
        self.description = ""
        self.editable_id = False


class ModelXnatNewProject:
    def __init__(self):
        self.data = XnatNewProjectData()
