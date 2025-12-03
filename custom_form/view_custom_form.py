import flet as ft

class ViewCustomForm(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # ----- Graphical elements -----
        self.title = None
        # top level
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        # xnat dropdowns
        self.dd_xnat_project = None
        self.dd_xnat_subject = None
        self.dd_xnat_experiment = None
        # custom forms
        self.txt_group = None
        self.txt_timepoint = None
        self.txt_dose = None
        # button home/back save
        self.btn_home_back = None
        self.btn_save = None
        # progressbar
        self.pb_custom_form = None
        self.dlg_custom_form = None
        # dialog
        self._dlg_auth = None

        # layout
        self._main_layout = None

    # ------------------------------------------------------
    # AUTH DIALOG
    # ------------------------------------------------------
    def open_auth_dialog(self, dlg):
        self._dlg_auth = dlg
        self._page.open(dlg)
        self._page.update()

    def close_auth_dialog(self):
        if self._dlg_auth:
            self._page.close(self._dlg_auth)
            self._dlg_auth = None
            self._page.update()

    # ------------------------------------------------------
    # BUILD CUSTOM FORM
    # -----------------------------------------------------
    def build_interface(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self._main_layout

    def _build_controls(self):
        """Graphical elements"""
        # button style
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLUE_900,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
        )

        # title
        self.title = ft.Row(
            [
                ft.Icon(
                    ft.Icons.DATASET,
                    size=36,
                    color=ft.Colors.BLUE_700
                ),
                ft.Text(
                    "XNAT-PIC Custom Form",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # level buttons: project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            text="Project",
            width=200,
            tooltip="Select the project where to save the custom forms",
            style=btn_style
        )
        self.btn_subject = ft.ElevatedButton(
            text="Subject",
            width=200,
            tooltip="Select the subject where to save the custom forms",
            style=btn_style
        )
        self.btn_experiment = ft.ElevatedButton(
            text="Experiment",
            width=200,
            tooltip="Select the experiment where to save the custom forms",
            style=btn_style
        )

        # xnat dropdowns project, subject, experiment
        self.dd_xnat_project = ft.Dropdown(
            hint_text="Project",
            width=200,
            prefix_icon=ft.Icons.DASHBOARD,
        )
        self.dd_xnat_subject = ft.Dropdown(
            hint_text="Subject",
            width=200,
            prefix_icon=ft.Icons.PERSON,
        )
        self.dd_xnat_experiment = ft.Dropdown(
            hint_text="Experiment",
            width=200,
            prefix_icon=ft.Icons.SCIENCE,
        )

        # custom_forms
        self.txt_group = ft.TextField(label="Group",
                                      hint_text="Please enter group here",
                                      width=200, )
        self.txt_timepoint = ft.TextField(label="Timepoint",
                                          hint_text="Please enter timepoint here",
                                          width=200, )
        self.txt_dose = ft.TextField(label="Dose",
                                     hint_text="Please enter dose here",
                                     width=200, )

        # buttons home/back and upload
        self.btn_home_back = ft.ElevatedButton(
            "Home",
            icon=ft.Icons.ARROW_BACK,
            style=btn_style,
        )
        self.btn_save = ft.ElevatedButton(
            "Save",
            icon=ft.Icons.DATASET,
            style=btn_style,
        )

        # progressbar dialog
        self.pb_custom_form = ft.ProgressBar(width=250)
        self.dlg_custom_form = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_custom_form,
        )

    def _bind_events(self):
        """Bind events"""
        self.btn_project.on_click = self._controller.custom_forms_project
        self.btn_subject.on_click = self._controller.custom_forms_subject
        self.btn_experiment.on_click = self._controller.custom_forms_experiment
        self.dd_xnat_project.on_change = self._controller.on_project_selected
        self.dd_xnat_subject.on_change = self._controller.on_subject_selected
        self.dd_xnat_experiment.on_change = \
            self._controller.on_experiment_selected
        self.btn_home_back.on_click = self._controller.on_home_back_clicked

    def _define_layout(self):
        """Define layout"""
        row_top = ft.Row(
            [
                self.btn_project,
                self.btn_subject,
                self.btn_experiment,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        row_dd = ft.Row(
            [
                self.dd_xnat_project,
                self.dd_xnat_subject,
                self.dd_xnat_experiment,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        row_custom_form = ft.Row(
            [
                self.txt_group,
                self.txt_timepoint,
                self.txt_dose,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        row_home_upload = ft.Row(
            [self.btn_home_back, self.btn_save],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self._main_layout = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.title,
                row_top,
                row_dd,
                row_custom_form,
                row_home_upload,
            ]
        )

    # ------------------------------------------------------
    # INITIAL STATE
    # ------------------------------------------------------
    def set_initial_state(self):
        # Enable top-level
        self.btn_project.disabled = False
        self.btn_subject.disabled = False
        self.btn_experiment.disabled = False

        # Disable the other controls
        for c in [
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment,
            self.txt_group,
            self.txt_timepoint,
            self.txt_dose,
            self.btn_save,
        ]:
            c.disabled = True

        # Reset home/back
        self.btn_home_back.text = "Home"
        self.btn_home_back.disabled = False

        # Reset dropdowns
        for dd in [
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment
        ]:
            dd.options = []
            dd.hint_text = "Select"
            dd.value = None

        # Reset custom forms
        self.txt_group.value = ""
        self.txt_timepoint.value = ""
        self.txt_dose.value = ""

        self._page.update()

    # ------------------------------------------------------
    # LEVEL MODE
    # ------------------------------------------------------
    def set_mode(
            self,
            level_buttons_enabled,
            save_enabled,
            dd_project,
            dd_subject,
            dd_experiment,
            custom_field_text,
    ):
        # enable/disable top-level
        for c in [
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
        ]:
            c.disabled = not level_buttons_enabled

        # dropdown project, subject, experiment in xnat
        self.dd_xnat_project.disabled = not dd_project
        self.dd_xnat_subject.disabled = not dd_subject
        self.dd_xnat_experiment.disabled = not dd_experiment

        # enable/disable custom form text
        for c in [
            self.txt_group,
            self.txt_timepoint,
            self.txt_dose,
        ]:
            c.disabled = not custom_field_text

        # save
        self.btn_save.disabled = not save_enabled

        # home/back
        if self.btn_home_back:
            self.btn_home_back.text = "Back"

        self._page.update()

    # ------------------------------------------------------
    # FILL DROPDOWN WITH VALUES READ IN XNAT
    # ------------------------------------------------------
    def reset_dropdown(self, dd):
        dd.options = []
        dd.value = None

    def populate_projects(self, projects):
        self.dd_xnat_project.options = [
            ft.dropdown.Option(key=p["id"], text=p["label"]) for p in projects
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
            ft.dropdown.Option(key=e["id"], text=e["label"]) for e in
            experiments
        ]
        self.dd_xnat_experiment.value = None
        self._page.update()

    # ------------------------------------------------------
    # SET CUSTOM FIELDS
    # ------------------------------------------------------
    def set_custom_fields(self, group="", timepoint="", dose=""):
        self.txt_group.value = group or ""
        self.txt_timepoint.value = timepoint or ""
        self.txt_dose.value = dose or ""
        self._page.update()

    # ------------------------------------------------------
    # UTILITY
    # ------------------------------------------------------
    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

    @property
    def page(self):
        return self._page

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller