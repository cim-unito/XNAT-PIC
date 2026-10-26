import flet as ft

class XnatDropdownMixin:
    def __init__(self):
        self._page = None
        self.dd_xnat_project = None
        self.dd_xnat_subject = None
        self.dd_xnat_experiment = None

    def populate_projects(self, projects):
        self.dd_xnat_project.options = [
            ft.dropdown.Option(key=p["id"], text=p["name"]) for p in projects
        ]
        self.dd_xnat_project.value = None

        self.reset_dropdown(self.dd_xnat_subject)
        self.reset_dropdown(self.dd_xnat_experiment)

        self._page.update()

    def populate_subjects(self, subjects):
        self.dd_xnat_subject.options = [
            ft.dropdown.Option(key=s["id"], text=s["label"]) for s in subjects
        ]
        self.dd_xnat_subject.value = None

        self.reset_dropdown(self.dd_xnat_experiment)

        self._page.update()

    def populate_experiments(self, experiments):
        self.dd_xnat_experiment.options = [
            ft.dropdown.Option(key=e["id"], text=e["label"]) for e in experiments
        ]
        self.dd_xnat_experiment.value = None
        self._page.update()

    @staticmethod
    def reset_dropdown(dd):
        dd.options = []
        dd.value = None