import flet as ft

from shared_ui.ui.base_view import BaseView, AuthDialogMixin, XnatDropdownMixin
from shared_ui.ui.button import Button
from shared_ui.ui.header import build_header
from shared_ui.ui.palette import Palette, default_palette
from shared_ui.ui.section_card import build_section_card


class ViewCustomForm(BaseView, AuthDialogMixin, XnatDropdownMixin):
    def __init__(self, page: ft.Page):
        super().__init__(page)
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

        # palette
        self.palette = default_palette()

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
        btn_style = Button.create_button_style(self.palette)

        # title
        self.title = build_header(
            title="XNAT-PIC Custom Form",
            icon=ft.Icons.DATASET,
            palette=self.palette,
        )

        # level buttons: project, subject, experiment
        self.btn_project = Button.build_text_button(
            "Project",
            btn_style,
            tooltip="Select the project where to save the custom forms",
        )
        self.btn_subject = Button.build_text_button(
            "Subject",
            btn_style,
            tooltip="Select the subject where to save the custom forms",

        )
        self.btn_experiment = Button.build_text_button(
            "Experiment",
            btn_style,
            tooltip="Select the experiment where to save the custom forms",
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
        self.btn_home_back = Button.build_text_button(
            "Home",
            btn_style,
            icon=self.icon_home_back,
            text_control=self.txt_home_back,
        )
        self.btn_save = Button.build_text_button(
            "Save",
            btn_style,
            icon=ft.Icon(ft.Icons.DATASET, size=26),
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

        setup_card = build_section_card(
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
            palette=self.palette,
        )

        form_card = build_section_card(
            title="Custom form data",
            description="Fill in the group, timepoint, and dose values.",
            icon=ft.Icons.TEXT_FIELDS,
            content=row_custom_form,
            palette=self.palette,
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
        self.set_home_back_state("Home", ft.Icons.HOME, enabled=True)

        # Reset dropdowns
        self.reset_dropdowns([
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment,
        ])

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
        self.set_home_back_state("Back", ft.Icons.ARROW_BACK, enabled=True)

        self._page.update()

    # ------------------------------------------------------
    # SET CUSTOM FIELDS
    # ------------------------------------------------------
    def set_custom_fields(self, group="", timepoint="", dose=""):
        self.txt_group.value = group or ""
        self.txt_timepoint.value = timepoint or ""
        self.txt_dose.value = dose or ""
        self._page.update()


    @staticmethod
    def _create_default_palette() -> Palette:
        return default_palette()