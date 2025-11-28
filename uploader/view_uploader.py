import flet as ft


class ViewUploader(ft.Control):
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
        self.btn_file = None
        # file selection group
        self.file_picker = None
        self.btn_select_folder = None
        self.tree_view_dcm = None
        self.img_preview = None
        self.btn_show_tags = None
        self.cnt_modify_modality = None
        self.btn_modify_modality = None
        self.dd_modify_modality = None
        # xnat dropdowns + new buttons
        self.dd_xnat_project = None
        self.dd_xnat_subject = None
        self.dd_xnat_experiment = None
        self.btn_new_project = None
        self.btn_new_subject = None
        self.btn_new_experiment = None
        # button home/back upload
        self.btn_home_back = None
        self.btn_upload = None
        # progressbar
        self.pb_upload = None
        self.dlg_upload = None
        # dialog
        self._dlg_auth = None
        self.dlg_modality = None

        # layout
        self._main_layout = None

        self.selected_file = None
        self.selected_folders = set()

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
    # BUILD UPLOADER INTERFACE
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
                    ft.Icons.CLOUD_UPLOAD,
                    size=36,
                    color=ft.Colors.BLUE_700
                ),
                ft.Text(
                    "XNAT-PIC Uploader",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # level buttons: project, subject, experiment, file
        self.btn_project = ft.ElevatedButton(
            text="Project",
            width=200,
            tooltip="Select the project to upload",
            style=btn_style
        )
        self.btn_subject = ft.ElevatedButton(
            text="Subject",
            width=200,
            tooltip="Select the subject to upload",
            style=btn_style
        )
        self.btn_experiment = ft.ElevatedButton(
            text="Experiment",
            width=200,
            tooltip="Select the experiment to upload",
            style=btn_style
        )
        self.btn_file = ft.ElevatedButton(
            text="File",
            width=200,
            tooltip="Select the file to upload",
            style=btn_style
        )

        # button select folder
        self.file_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)
        self.btn_select_folder = ft.ElevatedButton(
            text="Select folder",
            icon=ft.Icons.FOLDER_OPEN,
            style=btn_style,
        )

        # treeview
        self.tree_view_dcm = ft.Container(
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

        # image preview
        self.img_preview = ft.Image(
            src="assets/images/ImagePreview.png",
            width=260,
            height=260,
            fit=ft.ImageFit.CONTAIN,
            border_radius=12,
        )

        # button show dicom tags and modify modality
        self.btn_show_tags = ft.ElevatedButton(
            "Show DICOM tags",
            icon=ft.Icons.LIST_ALT,
            style=btn_style,
        )

        # button and dropdown modify modality
        self.cnt_modify_modality = ft.Column()
        self.btn_modify_modality = ft.ElevatedButton(
            "Modify DICOM modality",
            icon=ft.Icons.BUILD,
            style=btn_style,
        )
        self.dd_modify_modality = ft.Dropdown(
            options=[
                ft.dropdown.Option("MR"),
                ft.dropdown.Option("US"),
                ft.dropdown.Option("OI"),
                ft.dropdown.Option("OA"),
            ],
            hint_text="New Modality",
            width=200,
        )
        self.cnt_modify_modality.controls.append(self.btn_modify_modality)

        # xnat dropdowns project, subject, experiment
        self.dd_xnat_project = ft.Dropdown(
            hint_text="Project",
            width=200,
        )
        self.dd_xnat_subject = ft.Dropdown(
            hint_text="Subject",
            width=200,
        )
        self.dd_xnat_experiment = ft.Dropdown(
            hint_text="Experiment",
            width=200,
        )

        # xnat new project, subject, experiment
        self.btn_new_project = ft.ElevatedButton(
            "New Project",
            icon=ft.Icons.ADD_BOX,
            style=btn_style,
        )
        self.btn_new_subject = ft.ElevatedButton(
            "New Subject",
            icon=ft.Icons.PERSON_ADD,
            style=btn_style,
        )
        self.btn_new_experiment = ft.ElevatedButton(
            "New Experiment",
            icon=ft.Icons.ADD_CHART,
            style=btn_style,
        )

        # button home/back and upload
        self.btn_home_back = ft.ElevatedButton(
            "Home",
            icon=ft.Icons.ARROW_BACK,
            style=btn_style,
        )
        self.btn_upload = ft.ElevatedButton(
            "Upload",
            icon=ft.Icons.CLOUD_UPLOAD,
            style=btn_style,
        )

        # progressbar dialog
        self.pb_upload = ft.ProgressBar(width=250)
        self.dlg_upload = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_upload,
        )

    def _bind_events(self):
        """Bind events"""
        self.btn_project.on_click = self._controller.upload_project
        self.btn_subject.on_click = self._controller.upload_subject
        self.btn_experiment.on_click = self._controller.upload_experiment
        self.btn_file.on_click = self._controller.upload_file
        self.file_picker.on_result = self.file_picker_result
        self.btn_select_folder.on_click = lambda \
                e: self.file_picker.get_directory_path()
        self.btn_show_tags.on_click = self._controller.on_show_tags_clicked
        self.btn_modify_modality.on_click = self._controller.modify_modality
        self.dd_modify_modality.on_change = self._controller.on_select_modality
        self.dd_xnat_project.on_change = self._controller.on_project_selected
        self.dd_xnat_subject.on_change = self._controller.on_subject_selected
        self.btn_new_project.on_click = self._controller.create_new_project
        self.btn_home_back.on_click = self._controller.on_home_back_clicked
        self.btn_upload.on_click = self._controller.dicom_upload

    def _define_layout(self):
        """Define layout"""
        row_top = ft.Row(
            [
                self.btn_project,
                self.btn_subject,
                self.btn_experiment,
                self.btn_file,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        col_tools = ft.Column(
            [
                self.btn_show_tags,
                self.cnt_modify_modality,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        col_preview = ft.Row(
            [
                self.img_preview,
                col_tools,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        row_file = ft.Row(
            [
                self.btn_select_folder,
                self.tree_view_dcm,
                ft.Container(col_preview, expand=True),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
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

        row_new = ft.Row(
            [
                self.btn_new_project,
                self.btn_new_subject,
                self.btn_new_experiment,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        row_home_upload = ft.Row(
            [self.btn_home_back, self.btn_upload],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # ----- Local Section -----
        local_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                            expand=True),
                        ft.Icon(ft.Icons.COMPUTER, size=22,
                                color=ft.Colors.BLUE_800),
                        ft.Text(
                            "Upload from your PC...",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                        ft.Container(
                            ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                            expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                row_file,
            ],
            spacing=20,
        )

        # ----- XNAT Section -----
        xnat_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                            expand=True),
                        ft.Icon(ft.Icons.CLOUD, size=22,
                                color=ft.Colors.BLUE_800),
                        ft.Text(
                            "...to XNAT",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                        ft.Container(
                            ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                            expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                row_dd,
                row_new,
            ],
            spacing=20,
        )

        # ---- SCROLLABLE CONTENT ----
        scrollable_content = ft.Container(
            content=ft.Column(
                [
                    row_top,
                    local_section,
                    xnat_section,
                ],
                spacing=32,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
        )

        # ---- MAIN LAYOUT ----
        self._main_layout = ft.Column(
            [
                self.title,
                ft.Container(scrollable_content, expand=True),
                row_home_upload,
            ],
            spacing=20,
            expand=True,
        )

    # ------------------------------------------------------
    # INITIAL STATE
    # ------------------------------------------------------
    def set_initial_state(self):
        # Enable top-level
        self.btn_project.disabled = False
        self.btn_subject.disabled = False
        self.btn_experiment.disabled = False
        self.btn_file.disabled = False

        # Disable the other controls
        for c in [
            self.btn_select_folder,
            self.btn_show_tags,
            self.btn_modify_modality,
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment,
            self.btn_new_project,
            self.btn_new_subject,
            self.btn_new_experiment,
            self.btn_upload,
        ]:
            c.disabled = True

        # Reset home/back
        self.btn_home_back.text = "Home"
        self.btn_home_back.disabled = False

        # Reset internal state
        self.selected_file = None
        self.selected_folders = set()

        # Reset dropdowns
        self.dd_xnat_project.value = None
        self.dd_xnat_project.options = []

        self.dd_xnat_subject.value = None
        self.dd_xnat_subject.options = []

        self.dd_xnat_experiment.value = None
        self.dd_xnat_experiment.options = []

        # Reset preview & tree
        self.tree_view_dcm.content.controls.clear()
        self._controller.preview_cache.clear()
        self.img_preview.src_base64 = None
        self.img_preview.src_bytes = None
        self.img_preview.src = None
        self.img_preview.src = "assets/images/ImagePreview.png"

        # Modality dropdown reset
        self.cnt_modify_modality.controls.clear()
        self.cnt_modify_modality.controls.append(self.btn_modify_modality)
        self.dd_modify_modality.value = None

        self._page.update()

    # ------------------------------------------------------
    # LEVEL MODE
    # ------------------------------------------------------
    def set_mode(
            self,
            level_buttons_enabled,
            select_group_enabled,
            upload_enabled,
            dd_project,
            dd_subject,
            dd_experiment,
            new_project,
            new_subject,
            new_experiment,
    ):
        # enable/disable top-level
        for c in [
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
            self.btn_file,
        ]:
            c.disabled = not level_buttons_enabled

        # select folder / tree / preview / show tags viaggiano insieme
        for c in [
            self.btn_select_folder,
            self.btn_show_tags,
            self.btn_modify_modality,
        ]:
            c.disabled = not select_group_enabled

        # dropdown project, subject, experiment in xnat
        self.dd_xnat_project.disabled = not dd_project
        self.dd_xnat_subject.disabled = not dd_subject
        self.dd_xnat_experiment.disabled = not dd_experiment

        # new project, subject, experiment buttons
        self.btn_new_project.disabled = not new_project
        self.btn_new_subject.disabled = not new_subject
        self.btn_new_experiment.disabled = not new_experiment

        # upload
        self.btn_upload.disabled = not upload_enabled

        # home/back
        if self.btn_home_back:
            self.btn_home_back.text = "Back"

        self._page.update()

    # ------------------------------------------------------
    # FILE PICKER
    # ------------------------------------------------------
    def file_picker_result(self, e):
        # if e.path:
        #     self._controller.get_directory_to_upload(e.path)
        # else:
        #     self.create_alert("No folder selected.")
        pass

    # ------------------------------------------------------
    # TREEVIEW
    # ------------------------------------------------------
    def build_lazy_tree(self, items, expand_callback, file_selected_callback):
        tiles = []
        for it in items:
            if it["is_dir"]:
                tiles.append(self.make_lazy_folder(it, expand_callback))
            else:
                tiles.append(self.make_file_tile(it, file_selected_callback))
        return ft.ListView(tiles, expand=True, spacing=2)

    def make_lazy_folder(self, item, expand_callback):
        return ft.ExpansionTile(title=ft.Text(item["name"]),
                                leading=ft.Icon(ft.Icons.FOLDER),
                                controls=[ft.Text("Loading...")],
                                on_change=lambda e, p=item[
                                    "path"]: expand_callback(e, p,
                                                             e.control), )

    def make_file_tile(self, item, file_selected_callback):
        change_color = (
            ft.Colors.YELLOW_200
            if self.selected_file == item["path"]
            else ft.Colors.WHITE
        )
        return ft.ListTile(
            title=ft.Text(item["name"]),
            leading=ft.Icon(ft.Icons.DESCRIPTION),
            bgcolor=change_color,
            on_click=lambda e, p=item["path"]: file_selected_callback(p),
        )

    def update_tree(self, tree_widget):
        self.tree_view_dcm.content = tree_widget
        self._page.update()

    def highlight_selected_file(self, filepath: str):
        self.selected_file = filepath
        self._page.update()

    def highlight_folder(self, path: str):
        if path in self.selected_folders:
            self.selected_folders.remove(path)
        else:
            self.selected_folders.add(path)
        self._page.update()

    # ------------------------------------------------------
    # PREVIEW IMAGE
    # ------------------------------------------------------
    def set_image_preview(self, b64: str):
        self.img_preview.src_base64 = b64
        self.img_preview.update()

    # ------------------------------------------------------
    # SHOW DICOM TAGS
    # ------------------------------------------------------
    def show_dicom_tags_dialog(self, tags):
        rows = []
        for elem in tags:
            rows.append(
                ft.Row(
                    controls=[
                        ft.Text(str(elem["tag"]), width=120),
                        ft.Text(elem["name"], width=200),
                        ft.Text(elem["value"], width=350),
                    ]
                )
            )

        dlg = ft.AlertDialog(
            title=ft.Text("DICOM Tags"),
            content=ft.Container(
                ft.ListView(rows, expand=True),
                width=700,
                height=450,
            ),
            actions=[ft.TextButton("Close",
                                   on_click=lambda e: self._page.close(dlg))],
            modal=True,
        )
        self._page.open(dlg)
        self._page.update()

    # ------------------------------------------------------
    # OT Modality
    # ------------------------------------------------------
    def show_upload_ot_modality(self):
        self.dlg_modality = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text(
                "In your dataset there are DICOMs with Modality OT."
                "Upload to XNAT anyway?"),
            actions=[
                ft.TextButton("Yes",
                              on_click=lambda
                                  e: self._controller.upload_ot_modality()),
                ft.TextButton("No", on_click=lambda
                    e: self._page.close(self.dlg_modality)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.open(self.dlg_modality)
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
    # PROGRESSBAR / ALERT
    # ------------------------------------------------------
    def show_progress_dialog(self):
        self._page.open(self.dlg_upload)
        self._page.update()

    def update_progress(self, value):
        self.pb_upload.value = value
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