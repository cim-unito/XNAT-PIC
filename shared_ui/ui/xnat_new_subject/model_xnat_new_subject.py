class XnatNewSubjectData:
    def __init__(self):
        self.title = ""
        self.subject_id = ""
        self.accessibility = "private"
        self.description = ""
        self.editable_id = False

    def reset(self):
        self.title = ""
        self.subject_id = ""
        self.accessibility = "private"
        self.description = ""
        self.editable_id = False

class ModelXnatNewSubject:
    def __init__(self):
        self.data = XnatNewSubjectData()

    def reset(self):
        self.data.reset()
