import flet as ft

from shared_ui.ui.buttons import Buttons
from shared_ui.ui.palette import Palette

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
        self.txt_home_back = None
        self.icon_home_back = None
        self.btn_save = None
        # progressbar
        self.pb_custom_form = None
        self.dlg_custom_form = None
        # dialog
        self._dlg_auth = None

        # layout
        self._main_layout = None

        # palette
        self.palette = self._create_default_palette()

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
        btn_style = Buttons().create_button_style(self.palette)

        # title
        self.title = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=16,
                        bgcolor=self.palette.surface_stronger,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            ft.Icons.DATASET,
                            size=30,
                            color=self.palette.primary,
                        ),
                    ),
                    ft.Text(
                        value="XNAT-PIC Custom Form",
                        size=32,
                        weight=ft.FontWeight.W_700,
                        color=self.palette.primary_text,
                        font_family="Inter",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            bgcolor=self.palette.surface,
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            border_radius=20,
        )

        # level buttons: project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(
                        value="Project",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        font_family="Inter",
                    ),
                ],
            ),
            tooltip="Select the project where to save the custom forms",
            style=btn_style,
            expand=True,
        )
        self.btn_subject = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(
                        value="Subject",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        font_family="Inter",
                    ),
                ],
            ),
            tooltip="Select the subject where to save the custom forms",
            style=btn_style,
            expand=True,
        )
        self.btn_experiment = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(
                        value="Experiment",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        font_family="Inter",
                    ),
                ],
            ),
            tooltip="Select the experiment where to save the custom forms",
            style=btn_style,
            expand=True,
        )

        # xnat dropdowns project, subject, experiment
        self.dd_xnat_project = ft.Dropdown(
            hint_text="Project",
            prefix_icon=ft.Icons.DASHBOARD,
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )
        self.dd_xnat_subject = ft.Dropdown(
            hint_text="Subject",
            prefix_icon=ft.Icons.PERSON,
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )
        self.dd_xnat_experiment = ft.Dropdown(
            hint_text="Experiment",
            prefix_icon=ft.Icons.SCIENCE,
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )

        # custom_forms
        self.txt_group = ft.TextField(
            label="Group",
            hint_text="Please enter group here",
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )
        self.txt_timepoint = ft.TextField(
            label="Timepoint",
            hint_text="Please enter timepoint here",
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )
        self.txt_dose = ft.TextField(
            label="Dose",
            hint_text="Please enter dose here",
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )

        # buttons home/back and upload
        self.txt_home_back = ft.Text(
            value="Home",
            size=16,
            weight=ft.FontWeight.W_600,
            font_family="Inter",
        )
        self.icon_home_back = ft.Icon(ft.Icons.HOME, size=26)
        self.btn_home_back = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    self.icon_home_back,
                    self.txt_home_back,
                ],
            ),
            style=btn_style,
            expand=True,
        )
        self.btn_save = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.DATASET, size=26),
                    ft.Text(
                        value="Save",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        font_family="Inter",
                    ),
                ],
            ),
            style=btn_style,
            expand=True,
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
        self.btn_save.on_click = self._controller.on_save_clicked
        self.btn_home_back.on_click = self._controller.on_home_back_clicked

    def _define_layout(self):
        """Define layout"""
        header_section = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                self.title,
            ],
        )

        row_top = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=12,
            spacing=12,
            controls=[
                ft.Container(col={"xs": 12, "sm": 4}, content=self.btn_project),
                ft.Container(col={"xs": 12, "sm": 4}, content=self.btn_subject),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.btn_experiment,
                ),
            ],
        )

        row_dd = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=12,
            spacing=12,
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.dd_xnat_project,
                ),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.dd_xnat_subject,
                ),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.dd_xnat_experiment,
                ),
            ],
        )

        row_custom_form = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=12,
            spacing=12,
            controls=[
                ft.Container(col={"xs": 12, "sm": 4}, content=self.txt_group),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.txt_timepoint,
                ),
                ft.Container(col={"xs": 12, "sm": 4}, content=self.txt_dose),
            ],
        )

        setup_card = self._build_section_card(
            title="XNAT selection",
            description=(
                "Choose the level and select the project, subject, and "
                "experiment in XNAT."
            ),
            icon=ft.Icons.TUNE,
            content=ft.Column(
                spacing=12,
                controls=[
                    row_top,
                    row_dd,
                ],
            ),
        )

        form_card = self._build_section_card(
            title="Custom form data",
            description="Fill in the group, timepoint, and dose values.",
            icon=ft.Icons.TEXT_FIELDS,
            content=row_custom_form,
        )

        row_home_upload = ft.Row(
            [self.btn_home_back, self.btn_save],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self._main_layout = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=28, vertical=18),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18,
                controls=[
                    header_section,
                    setup_card,
                    form_card,
                    ft.Container(expand=True),
                    row_home_upload,
                ],
            ),
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
        if self.txt_home_back:
            self.txt_home_back.value = "Home"
        if self.icon_home_back:
            self.icon_home_back.name = ft.Icons.HOME
        self.btn_home_back.disabled = False

        # Reset dropdowns
        for dd in [
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment
        ]:
            dd.options = []
            dd.key = "Select"
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
        if self.txt_home_back:
            self.txt_home_back.value = "Back"
        if self.icon_home_back:
            self.icon_home_back.name = ft.Icons.ARROW_BACK

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

    def _build_section_card(
            self,
            title: str,
            description: str,
            icon: str,
            content: ft.Control,
    ) -> ft.Control:
        return ft.Container(
            content=ft.Card(
                color=self.palette.surface,
                surface_tint_color=self.palette.primary,
                elevation=3,
                shape=ft.RoundedRectangleBorder(radius=18),
                content=ft.Container(
                    padding=18,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=36,
                                        height=36,
                                        border_radius=10,
                                        bgcolor=self.palette.surface_stronger,
                                        alignment=ft.alignment.center,
                                        content=ft.Icon(
                                            icon,
                                            size=20,
                                            color=self.palette.primary,
                                        ),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                title,
                                                size=16,
                                                weight=ft.FontWeight.W_600,
                                                color=self.palette.primary_text,
                                                font_family="Inter",
                                            ),
                                            ft.Text(
                                                description,
                                                size=12,
                                                color=self.palette.subtle_text,
                                                font_family="Inter",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            content,
                        ],
                    ),
                ),
            ),
        )

    @staticmethod
    def _create_default_palette() -> Palette:
        return Palette(
            primary=ft.Colors.BLUE_600,
            primary_hover=ft.Colors.BLUE_700,
            primary_pressed=ft.Colors.BLUE_800,
            primary_text=ft.Colors.BLUE_900,
            surface=ft.Colors.BLUE_50,
            surface_stronger=ft.Colors.BLUE_100,
            subtle_text="#475569",
        )