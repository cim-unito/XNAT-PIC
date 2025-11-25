import flet as ft


class ViewConverter(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.dd_conversion_type = None
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        self.sw_existing_folder = None
        self.sw_copy_files = None
        self.btn_select_folder = None
        self.file_picker = None
        self.tree_view = None
        self.tree_view_dcm = None
        self.btn_go_home = None
        self.btn_convert = None
        self.pb_conversion = None
        self.dlg_conversion = None

    def build_interface(self):
        # Define controls
        # title
        self._title = ft.Row(
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

        # Button style
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLUE_900,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
        )
        self.dd_conversion_type = ft.Dropdown(
            label="Conversion type",
            on_change=self._controller.conversion_type,
            options=[
                ft.dropdown.Option("Bruker2DICOM"),
                ft.dropdown.Option("IVIS2DICOM"),
            ],
            width=200
        )
        # buttons project, subject, experiment
        self.btn_project = ft.ElevatedButton(
            text="Convert Project",
            width=200,
            tooltip="Select the project to convert",
            on_click=self._controller.convert_project,
            style=btn_style
        )
        self.btn_subject = ft.ElevatedButton(
            text="Convert Subject",
            width=200,
            tooltip="Select the subject to convert",
            on_click=self._controller.convert_subject,
            style=btn_style
        )
        self.btn_experiment = ft.ElevatedButton(
            text="Convert Experiment",
            width=200,
            tooltip="Select the experiment to convert",
            on_click=self._controller.convert_experiment,
            style=btn_style
        )

        # switch
        self.sw_existing_folder = ft.Switch(
            label="Overwrite existing folders", value=False
        )
        self.sw_copy_files = ft.Switch(label="Copy additional files",
                                       value=False)

        # button select folder
        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self._page.overlay.append(self.file_picker)
        self.btn_select_folder = ft.ElevatedButton(
            "Select folder",
            icon=ft.Icons.FOLDER_OPEN,
            disabled=True,
            on_click=lambda e: self.file_picker.get_directory_path(),
            style=btn_style,
        )

        # treeview
        self.tree_view = ft.Container(
            width=250,
            height=320,
            content=ft.ListView([], expand=True, spacing=4),
            border_radius=10,
            padding=10,
            bgcolor=ft.Colors.BLUE_50,
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color=ft.Colors.BLUE_100,
            ),
        )

        self.tree_view_dcm = f= ft.Container(
            width=250,
            height=320,
            content=ft.ListView([], expand=True, spacing=4),
            border_radius=10,
            padding=10,
            bgcolor=ft.Colors.BLUE_50,
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color=ft.Colors.BLUE_100,
            ),
        )

        # button go home and convert
        self.btn_go_home = ft.ElevatedButton(
            text="Go home",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: self._controller.go_home(),
            style=btn_style,
        )
        self.btn_convert = ft.ElevatedButton(text="Convert",
                                             icon=ft.Icons.CHANGE_CIRCLE,
                                             on_click=self._controller.dicom_converter,
                                             style=btn_style,)

        # progressbar
        self.pb_conversion = ft.ProgressBar(width=300)
        self.dlg_conversion = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_conversion,
        )

        # Define layout
        row1 = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.dd_conversion_type,
                self.btn_project,
                self.btn_subject,
                self.btn_experiment,
            ],
        )

        row2 = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.tree_view,
                self.tree_view_dcm,
            ],
        )

        row3 = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.btn_go_home,
                self.btn_convert,
            ],
        )
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self._title,
                row1,
                self.sw_existing_folder,
                self.sw_copy_files,
                self.btn_select_folder,
                row2,
                row3,
            ],
        )

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._controller.get_directory_to_convert(e.path)
        else:
            self.create_alert("No folder selected!")

    def build_lazy_tree(self, items, expand_callback, file_selected_callback):
        tiles = []
        for item in items:
            if item["is_dir"]:
                tile = self.make_lazy_folder(item, expand_callback)
            else:
                tile = self.make_file_tile(item, file_selected_callback)
            tiles.append(tile)

        return ft.ListView(tiles, expand=True)

    def make_lazy_folder(self, item, expand_callback):
        dummy_child = ft.Text("Loading...")

        tile = ft.ExpansionTile(
            leading=ft.Icon(ft.Icons.FOLDER),
            title=ft.Text(item["name"]),
            controls=[dummy_child],
            on_change=lambda e, p=item["path"]: expand_callback(e, p, e.control),
        )
        return tile

    def make_file_tile(self, item, file_selected_callback):
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.DESCRIPTION),
            title=ft.Text(item["name"]),
            on_click=lambda e, p=item["path"]: file_selected_callback(p),
        )

    def update_tree(self, tree_widget, type_tree='src'):
        if type_tree == 'dcm':
            self.tree_view_dcm.content = tree_widget
        else:
            self.tree_view.content = tree_widget
        self._page.update()

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
