import flet as ft

from enums.tree_type import TreeType


class ViewConverter(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # ----- Graphical elements -----
        self.title = None
        # top level
        self.dd_conversion_type = None
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        # mid level
        self.sw_overwrite = None
        self.sw_copy_files = None
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

        # map enum → container
        self._tree_map: dict[TreeType, ft.Container] = {}
        self._selected_control = None

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
                    ft.Icons.CHANGE_CIRCLE,
                    size=36,
                    color=ft.Colors.BLUE_700
                ),
                ft.Text(
                    "XNAT-PIC Converter",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # dropdown conversion type
        self.dd_conversion_type = ft.Dropdown(
            options=[
                ft.dropdown.Option("Bruker2DICOM"),
                ft.dropdown.Option("IVIS2DICOM"),
            ],
            hint_text="Conversion type",
            width=200,

        )
        # level buttons: project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            text="Convert Project",
            width=200,
            tooltip="Select the project to convert",
            style=btn_style
        )
        self.btn_subject = ft.ElevatedButton(
            text="Convert Subject",
            width=200,
            tooltip="Select the subject to convert",
            style=btn_style
        )
        self.btn_experiment = ft.ElevatedButton(
            text="Convert Experiment",
            width=200,
            tooltip="Select the experiment to convert",
            style=btn_style
        )

        # switch
        self.sw_overwrite = ft.Switch(
            label="Overwrite existing folders",
        )
        self.sw_copy_files = ft.Switch(label="Copy additional files", )

        # button select folder
        self.file_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)
        self.btn_select_folder = ft.ElevatedButton(
            text="Select folder",
            icon=ft.Icons.FOLDER_OPEN,
            style=btn_style,
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
        self.btn_convert.on_click = self._controller.dicom_converter

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
                self.sw_copy_files,
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
            self.sw_copy_files,
            self.btn_select_folder,
            self.btn_convert,
        ]:
            c.disabled = True

        # reset home/back
        self.btn_home_back.text = "Home"
        self.btn_home_back.disabled = False

        # reset dropdown
        self.dd_conversion_type.value = ""

        # reset switch
        self.sw_overwrite.value = False
        self.sw_copy_files.value = False

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
            self.sw_copy_files,
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
    def file_picker_result(self, e):
        if e.path:
            self._controller.get_directory_to_convert(e.path)
        else:
            self.create_alert("No folder selected!")

    # -------------------------------------------------------
    # TREEVIEW RAW DATA/DICOM FILES
    # -------------------------------------------------------
    def map_tree_container(self, tree_type: TreeType,
                           container: ft.Container):
        """The container is placed in the map and contains the ListView inside."""
        self._tree_map[tree_type] = container

    def update_tree(self, new_widget: ft.ListView, tree_type: TreeType):
        """Update the content of the existing container"""
        container = self._tree_map.get(tree_type)
        container.content = new_widget
        self._page.update()

    # ----- Lazy tree builder -----
    def build_lazy_tree(self, items, expand_callback, file_selected_callback):
        tiles = [
            self._build_node(item, expand_callback, file_selected_callback)
            for item in items
        ]
        return ft.ListView(controls=tiles, expand=True)

    def _build_node(self, item, expand_callback, file_selected_callback):
        if item["is_dir"]:
            return self._make_lazy_folder(item, expand_callback)
        return self._make_file_tile(item, file_selected_callback)

    def _make_lazy_folder(self, item, expand_callback):
        return ft.ExpansionTile(
            leading=ft.Icon(ft.Icons.FOLDER),
            title=ft.Text(item["name"]),
            controls=[ft.Text("Loading...")],
            on_change=lambda e, path=item["path"]: expand_callback(
                e, path, e.control
            ),
        )

    def _make_file_tile(self, item, file_selected_callback):
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.DESCRIPTION),
            title=ft.Text(item["name"]),
            on_click=lambda e, path=item["path"]: file_selected_callback(e,
                                                                         path)
        )

    def update_expansion_tile(self, tile, children, expand_callback,
                              file_selected_callback):
        """ExpansionTile update already opened"""
        tile.controls.clear()

        if not children:
            tile.controls.append(ft.Text("Empty folder"))
        else:
            for item in children:
                node = self._build_node(item, expand_callback,
                                        file_selected_callback)
                tile.controls.append(node)

    def set_selected_control(self, control: ft.Control):
        """Highlight selected item"""
        if self._selected_control:
            self._clear_selection(self._selected_control)

        self._apply_selection(control)
        self._selected_control = control

    def _apply_selection(self, control: ft.Control):
        control.bgcolor = ft.Colors.AMBER_100

    def _clear_selection(self, control: ft.Control):
        control.bgcolor = None

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

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()
