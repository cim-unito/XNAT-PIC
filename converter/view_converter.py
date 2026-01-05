import flet as ft

from enums.tree_type import TreeType
from shared_ui.ui.buttons import Buttons
from shared_ui.ui.palette import Palette

class ViewConverter(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self.title = None
        # top level
        self.dd_conversion_type = None
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        # mid level
        self.sw_overwrite = None
        self.btn_select_folder = None
        self.file_picker = None
        self.tree_view_raw = None
        self.tree_view_dcm = None
        # bottom level
        self.btn_home_back = None
        self.btn_convert = None
        # progressbar
        self.pb_conversion = None
        self.dlg_conversion = None

        # layout
        self._main_layout = None

        # palette
        self.palette = self._create_default_palette()

        # map enum → container
        self._tree_map: dict[TreeType, ft.Container] = {}

    # ------------------------------------------------------
    # BUILD CONVERTER INTERFACE
    # -----------------------------------------------------
    def build_interface(self):
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self._main_layout

    def _build_controls(self):
        """Graphical elements"""
        btn_style = Buttons().create_button_style(self.palette)

        # title
        self.title = ft.Row(
            [
                ft.Icon(
                    ft.Icons.CHANGE_CIRCLE,
                    size=36,
                    color=self.palette.primary_text,
                ),
                ft.Text(
                    value="XNAT-PIC Converter",
                    size=36,
                    weight=ft.FontWeight.W_700,
                    color=self.palette.primary_text,
                    font_family="Inter",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # dropdown conversion type
        self.dd_conversion_type = ft.Dropdown(
            options=[
                ft.dropdown.Option("Bruker2Dicom"),
                ft.dropdown.Option("Ivis2Dicom"),
            ],
            hint_text="Conversion type",
            width=200,
            expand=True,

        )

        # level buttons: project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(value="Convert Project",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            width=200,
            expand=True,
            tooltip="Select the project to convert",
        )
        self.btn_subject = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(value="Convert Subject",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            width=200,
            expand=True,
            tooltip="Select the subject to convert",
        )
        self.btn_experiment = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(value="Convert Experiment",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            width=200,
            expand=True,
            tooltip="Select the experiment to convert",
        )

        # switch
        self.sw_overwrite = ft.Switch(
            label="Overwrite existing folders",
        )

        # button select folder
        self.file_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)
        self.btn_select_folder = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                    ft.Text(value="Select folder",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            font_family="Inter"),
                ],
            ),
            style=btn_style,
            width=200,
            expand=True,
            tooltip="Select the folder to convert",
        )
        # treeview raw data and dicom converted
        self.tree_view_raw = ft.Container(
            width=250,
            height=320,
            content=ft.ListView(controls=[], expand=True, spacing=4),
        )
        self.map_tree_container(TreeType.RAW, self.tree_view_raw)
        self.tree_view_dcm = ft.Container(
            width=250,
            height=320,
            content=ft.ListView(controls=[], expand=True, spacing=4),
        )
        self.map_tree_container(TreeType.DICOM, self.tree_view_dcm)

        # button home/back and convert
        self.btn_home_back = ft.ElevatedButton(
            text="Go home",
            icon=ft.Icons.ARROW_BACK,
            style=btn_style,
        )
        self.btn_convert = ft.ElevatedButton(text="Convert",
                                             icon=ft.Icons.CHANGE_CIRCLE,
                                             style=btn_style)

        # progressbar dialog
        self.pb_conversion = ft.ProgressBar(width=300)
        self.dlg_conversion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_conversion,
        )

    def _bind_events(self):
        """Bind events"""
        self.dd_conversion_type.on_change = self._controller.conversion_type
        self.btn_project.on_click = self._controller.convert_project
        self.btn_subject.on_click = self._controller.convert_subject
        self.btn_experiment.on_click = self._controller.convert_experiment
        self.file_picker.on_result = self.file_picker_result
        self.btn_select_folder.on_click = lambda \
                e: self.file_picker.get_directory_path()
        self.btn_home_back.on_click = self._controller.on_home_back_clicked
        self.btn_convert.on_click = self._controller.on_convert_clicked

    def _define_layout(self):
        """Define layout"""
        row_top = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.dd_conversion_type,
                self.btn_project,
                self.btn_subject,
                self.btn_experiment,
            ],
        )

        row_mid = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.tree_view_raw,
                self.tree_view_dcm,
            ],
        )

        row_bottom = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.btn_home_back,
                self.btn_convert,
            ],
        )

        self._main_layout = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.title,
                row_top,
                self.sw_overwrite,
                self.btn_select_folder,
                row_mid,
                row_bottom,
            ],
        )

    # ------------------------------------------------------
    # INITIAL STATE
    # ------------------------------------------------------
    def set_initial_state(self):
        """Set initial state"""
        # enable top-level
        self.dd_conversion_type.disabled = False
        self.btn_project.disabled = False
        self.btn_subject.disabled = False
        self.btn_experiment.disabled = False

        # disable the other controls
        for c in [
            self.sw_overwrite,
            self.btn_select_folder,
            self.btn_convert,
        ]:
            c.disabled = True

        # reset home/back
        self.btn_home_back.text = "Home"
        self.btn_home_back.disabled = False

        # reset dropdown
        self.dd_conversion_type.key = "Select"
        self.dd_conversion_type.value = None

        # reset switch
        self.sw_overwrite.value = False

        # reset treeview
        self.tree_view_raw.content.controls.clear()
        self.tree_view_dcm.content.controls.clear()

        self._page.update()

    # ------------------------------------------------------
    # LEVEL MODE
    # ------------------------------------------------------
    def set_mode(
            self,
            top_level_buttons_enabled,
            sw_enabled,
            select_folder_enabled,
            convert_enabled,
    ):
        # enable/disable top-level
        for c in [
            self.dd_conversion_type,
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
        ]:
            c.disabled = not top_level_buttons_enabled

        # enable/disable sw
        for c in [
            self.sw_overwrite,
        ]:
            c.disabled = not sw_enabled

        # enable/disable select folder
        for c in [
            self.btn_select_folder,
        ]:
            c.disabled = not select_folder_enabled

        # enable/disable convert
        self.btn_convert.disabled = not convert_enabled

        # enable/disable home/back
        if self.btn_home_back:
            self.btn_home_back.text = "Back"

        self._page.update()

    # ------------------------------------------------------
    # FILE PICKER
    # ------------------------------------------------------
    def file_picker_result(self, e: ft.FilePickerResultEvent):
        """
        Handle file picker result, delegating file processing to the
        controller; alert when no file is selected.
        """
        if e.path:
            self._controller.get_directory_to_convert(e.path)
        else:
            self.create_alert("No folder selected!")

    # -------------------------------------------------------
    # TREEVIEW RAW DATA/DICOM FILES
    # -------------------------------------------------------
    def map_tree_container(self, tree_type: TreeType,
                           container: ft.Container):
        """The container is placed in the tree map and contains the ListView inside."""
        self._tree_map[tree_type] = container

    def update_tree(self, new_widget: ft.ListView, tree_type: TreeType):
        """Update the content of the existing container"""
        container = self._tree_map.get(tree_type)
        container.content = new_widget
        self._page.update()

    # -------------------------------------------------------
    # PROGRESSBAR
    # -------------------------------------------------------
    def show_progress_dialog(self):
        self._page.open(self.dlg_conversion)
        self._page.update()

    def update_progress(self, value: float):
        self.pb_conversion.value = value
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, page):
        self.page = page

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

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