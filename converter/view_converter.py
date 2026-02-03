import flet as ft

from enums.converter_type import ConverterType
from enums.tree_type import TreeType
from shared_ui.ui.base_view import BaseView
from shared_ui.ui.buttons import Buttons
from shared_ui.ui.header import build_header
from shared_ui.ui.palette import Palette
from shared_ui.ui.section_card import build_section_card
from shared_ui.ui.theme import default_palette


class ViewConverter(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self.title = None
        # top level
        self.dd_conversion_type = None
        self.sw_overwrite = None
        self.file_picker = None
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        # mid level
        self.tree_view_raw = None
        self.tree_view_dcm = None
        self.tree_view_raw_list = None
        self.tree_view_dcm_list = None
        # bottom level
        self.btn_home_back = None
        self.txt_home_back = None
        self.icon_home_back = None
        self.btn_convert = None
        # progressbar
        self.pb_conversion = None
        self.dlg_conversion = None

        # layout
        self._main_layout = None

        # palette
        self.palette = default_palette()

        # map enum → container
        self._tree_map: dict[TreeType, ft.Container] = {}

    def build_interface(self):
        """Create and return the main layout for the converter view.

        This method instantiates all UI controls, binds events to the
        controller, defines the page layout, and resets the initial state
        so the view is ready for user interaction.
        """
        self._build_controls()
        self._bind_events()
        self._define_layout()
        self.set_initial_state()
        return self._main_layout

    def set_initial_state(self):
        """Reset the UI to the default idle state.

        Enables the top-level controls, disables the convert button, resets
        the home/back label and icon, clears tree views, and restores default
        dropdown/switch values.
        """
        # enable top-level
        for c in [
            self.dd_conversion_type,
            self.sw_overwrite,
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
        ]:
            c.disabled = False

        # disable the other controls
        self.btn_convert.disabled = True

        # reset home/back
        self.set_home_back_state("Home", ft.Icons.HOME, enabled=True)

        # reset dropdown
        self.reset_dropdowns([self.dd_conversion_type], reset_options=False)

        # reset switch
        self.sw_overwrite.value = False

        # reset treeview
        if self.tree_view_raw_list:
            self.tree_view_raw_list.controls.clear()
        if self.tree_view_dcm_list:
            self.tree_view_dcm_list.controls.clear()

        self._page.update()

    def set_mode(self):
        """Switch the UI to the active conversion mode.

        Disables top-level selection controls and enables conversion actions
        while toggling the home/back label to indicate a back navigation.
        """
        # disable top-level
        for c in [
            self.dd_conversion_type,
            self.sw_overwrite,
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
        ]:
            c.disabled = True

        # enable the other controls
        self.btn_convert.disabled = False

        # enable/disable home/back
        self.set_home_back_state("Back", ft.Icons.ARROW_BACK, enabled=True)

        self._page.update()

    def update_tree(self, new_widget: ft.ListView, tree_type: TreeType):
        """Replace the list view for the given tree type and refresh the UI."""
        container = self._tree_map.get(tree_type)
        container.content = new_widget
        if tree_type == TreeType.RAW:
            self.tree_view_raw_list = new_widget
        elif tree_type == TreeType.DICOM:
            self.tree_view_dcm_list = new_widget
        self._page.update()

    def show_progress_bar_dialog(self):
        """Display the modal progress dialog."""
        self._page.open(self.dlg_conversion)
        self._page.update()

    def update_progress_bar(self, value: float):
        """Update the progress bar value and refresh the page."""
        self.pb_conversion.value = value
        self._page.update()

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        """
        Handle file picker results and delegate processing to the controller.

        If a folder is selected, the controller is asked to process it;
        otherwise, the user is alerted and the view resets to the initial
        state.
        """
        if e.path:
            self._controller.get_directory_to_convert(e.path)
        else:
            self.create_alert("No folder selected!")
            self.set_initial_state()

    def _build_controls(self):
        """Instantiate and configure all UI controls used by the view."""
        btn_style = Buttons().create_button_style(self.palette)

        # title
        self.title = build_header(
            title="XNAT-PIC Converter",
            icon=ft.Icons.CHANGE_CIRCLE,
            palette=self.palette,
        )

        # dropdown conversion type
        self.dd_conversion_type = ft.Dropdown(
            options=[ft.dropdown.Option(ct.value) for ct in ConverterType],
            hint_text="Conversion type",
            expand=True,
            filled=True,
            bgcolor=self.palette.surface,
            border_radius=12,
        )

        # level buttons: project, subject, experiment
        self.btn_project = Buttons().build_text_button(
            "Convert Project",
            btn_style,
            tooltip="Select the project to convert",
        )
        self.btn_subject = Buttons().build_text_button(
            "Convert Subject",
            btn_style,
            tooltip="Select the subject to convert",
        )
        self.btn_experiment = Buttons().build_text_button(
            "Convert Experiment",
            btn_style,
            tooltip="Select the experiment to convert",
        )

        # switch overwrite existing folder
        self.sw_overwrite = ft.Switch(
            label="Overwrite existing folder",
        )

        # file picker
        self.file_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)

        # treeview raw data and dicom converted
        self.tree_view_raw_list = ft.ListView(
            controls=[],
            expand=True,
            spacing=4,
        )
        raw_list_container = ft.Container(
            expand=True,
            content=self.tree_view_raw_list,
        )
        self._map_tree_container(TreeType.RAW, raw_list_container)
        self.tree_view_raw = self._build_tree_panel(
            title="Raw data",
            icon=ft.Icons.FOLDER_OPEN,
            list_container=raw_list_container,
        )

        self.tree_view_dcm_list = ft.ListView(
            controls=[],
            expand=True,
            spacing=4,
        )
        dcm_list_container = ft.Container(
            expand=True,
            content=self.tree_view_dcm_list,
        )
        self._map_tree_container(TreeType.DICOM, dcm_list_container)
        self.tree_view_dcm = self._build_tree_panel(
            title="DICOM output",
            icon=ft.Icons.DOCUMENT_SCANNER,
            list_container=dcm_list_container,
        )

        # button home/back and convert
        self.txt_home_back = ft.Text(
            value="Go home",
            size=16,
            weight=ft.FontWeight.W_600,
            font_family="Inter",
        )
        self.icon_home_back = ft.Icon(ft.Icons.HOME, size=26)
        self.btn_home_back = Buttons().build_text_button(
            "Go home",
            btn_style,
            icon=self.icon_home_back,
            text_control=self.txt_home_back,
        )
        self.btn_convert = Buttons().build_text_button(
            "Convert",
            btn_style,
            icon=ft.Icon(ft.Icons.CHANGE_CIRCLE, size=26),
        )
        # progressbar dialog
        self.pb_conversion = ft.ProgressBar(width=300)
        self.dlg_conversion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_conversion,
        )

    def _bind_events(self):
        """Wire UI events to the controller callbacks."""
        self.dd_conversion_type.on_change = self._controller.conversion_type
        self.btn_project.on_click = self._controller.convert_project
        self.btn_subject.on_click = self._controller.convert_subject
        self.btn_experiment.on_click = self._controller.convert_experiment
        self.file_picker.on_result = self.file_picker_result
        self.btn_home_back.on_click = self._controller.on_home_back_clicked
        self.btn_convert.on_click = self._controller.on_convert_clicked

    def _define_layout(self):
        """Define layout"""
        header_section = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                self.title,
            ],
        )

        row_conversion_type = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=12,
            spacing=12,
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.dd_conversion_type,
                ),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.sw_overwrite,
                ),
                ft.Container(col={"xs": 12, "sm": 4}),
            ],
        )

        row_levels = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=12,
            spacing=12,
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.btn_project,
                ),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.btn_subject,
                ),
                ft.Container(
                    col={"xs": 12, "sm": 4},
                    content=self.btn_experiment,
                ),
            ],
        )

        row_mid = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=16,
            spacing=16,
            controls=[
                ft.Container(
                    col={"xs": 12, "md": 6},
                    content=self.tree_view_raw,
                ),
                ft.Container(
                    col={"xs": 12, "md": 6},
                    content=self.tree_view_dcm,
                ),
            ],
        )

        setup_card = build_section_card(
            title="Conversion setup",
            description=(
                "Select the conversion type, choose the folder to process, "
                "and set overwrite behavior."
            ),
            icon=ft.Icons.TUNE,
            content=ft.Column(
                spacing=12,
                controls=[
                    row_conversion_type,
                    row_levels,
                    row_mid,
                ],
            ),
            palette=self.palette,
        )

        action_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.btn_home_back,
                self.btn_convert,
            ],
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
                    ft.Container(expand=True),
                    action_row,
                ],
            ),
        )

    def _build_tree_panel(
            self,
            title: str,
            icon: str,
            list_container: ft.Container,
    ) -> ft.Control:
        return ft.Container(
            padding=12,
            bgcolor=self.palette.surface,
            border_radius=16,
            border=ft.border.all(1, self.palette.surface_stronger),
            height=280,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon, size=18, color=self.palette.primary),
                            ft.Text(
                                title,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=self.palette.primary_text,
                                font_family="Inter",
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=self.palette.surface_stronger),
                    list_container,
                ],
            ),
        )

    def _map_tree_container(self, tree_type: TreeType,
                            container: ft.Container):
        """
        Register the container that hosts a tree ListView for updates.
        """
        self._tree_map[tree_type] = container

    @staticmethod
    def _create_default_palette() -> Palette:
        return default_palette()

