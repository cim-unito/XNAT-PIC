import flet as ft


class ViewCustomForm(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        self._main_layout = None
        self._dlg_auth = None

        # Top-level buttons
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None

        # XNAT dropdowns + new
        self.dd_xnat_project = None
        self.dd_xnat_subject = None
        self.dd_xnat_experiment = None

        # Custom form
        self.txt_group = None
        self.txt_timepoint = None
        self.txt_dose = None

        # button home/back upload
        self.btn_home_back = None
        self.btn_save = None

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
    # UPLOADER INTERFACE
    # ------------------------------------------------------
    def build_interface(self):
        # title
        title = ft.Row(
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

        # Button style
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLUE_900,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
        )

        # Level buttons: project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            "Project",
            on_click=self._controller.upload_project,
            expand=True,
            style=btn_style
        )
        self.btn_subject = ft.ElevatedButton(
            "Subject",
            on_click=self._controller.upload_subject,
            expand=True,
            style=btn_style
        )
        self.btn_experiment = ft.ElevatedButton(
            "Experiment",
            on_click=self._controller.upload_experiment,
            expand=True,
            style=btn_style
        )

        row_levels = ft.Row(
            [
                self.btn_project,
                self.btn_subject,
                self.btn_experiment,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # xnat dropdowns project, subject, experiment
        self.dd_xnat_project = ft.Dropdown(
            hint_text="Project",
            width=200,
            disabled=True,
            prefix_icon=ft.Icons.DASHBOARD,
            on_change=self._controller.on_project_selected,
        )

        self.dd_xnat_subject = ft.Dropdown(
            hint_text="Subject",
            width=200,
            disabled=True,
            prefix_icon=ft.Icons.PERSON,
            on_change=self._controller.on_subject_selected,
        )

        self.dd_xnat_experiment = ft.Dropdown(
            hint_text="Experiment",
            width=200,
            disabled=True,
            prefix_icon=ft.Icons.SCIENCE,
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

        self.txt_group = ft.TextField(label="Group",
                                      hint_text="Please enter text here",
                                      width=200,)
        self.txt_timepoint = ft.TextField(label="Timepoint",
                                          hint_text="Please enter text here",
                                          width=200,)
        self.txt_dose = ft.TextField(label="Dose",
                                     hint_text="Please enter text here",
                                     width=200,)
        row_custom_form = ft.Row(
            [
                self.txt_group,
                self.txt_timepoint,
                self.txt_dose,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        # Buttons home/back and upload
        self.btn_home_back = ft.ElevatedButton(
            "Home",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._controller.on_home_back_clicked,
            style=btn_style,
        )

        self.btn_save = ft.ElevatedButton(
            "Save",
            icon=ft.Icons.DATASET,
            disabled=True,
            style=btn_style,
        )

        row_home_upload = ft.Row(
            [self.btn_home_back, self.btn_save],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Column(
            controls=[
                title,
                row_levels,
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
            self.btn_save,
        ]:
            c.disabled = True

        # Reset home/back
        self.btn_home_back.text = "Home"
        self.btn_home_back.disabled = False

        # Reset dropdowns
        self.dd_xnat_project.value = None
        self.dd_xnat_project.options = []

        self.dd_xnat_subject.value = None
        self.dd_xnat_subject.options = []

        self.dd_xnat_experiment.value = None
        self.dd_xnat_experiment.options = []

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

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    # ------------------------------------------------------
    # UTILITY
    # ------------------------------------------------------
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