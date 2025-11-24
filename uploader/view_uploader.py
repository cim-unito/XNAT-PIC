import flet as ft


class ViewUploader(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        self._main_layout = None
        self._dlg_auth = None

        self.selected_file = None
        self.selected_folders = set()

        # Top-level buttons
        self.btn_project = None
        self.btn_subject = None
        self.btn_experiment = None
        self.btn_file = None

        # File selection group
        self.file_picker = None
        self.btn_select_folder = None
        self.tree_view_dcm = None
        self.img_preview = None
        self.btn_show_tags = None
        self.cnt_modify_modality = None
        self.btn_modify_modality = None
        self.dd_modify_modality = None

        # XNAT dropdowns + new
        self.dd_xnat_project = None
        self.dd_xnat_subject = None
        self.dd_xnat_experiment = None

        self.btn_new_project = None
        self.btn_new_subject = None
        self.btn_new_experiment = None

        # bottom
        self.btn_home_back = None
        self.btn_upload = None

        # progressbar
        self.pb_upload = None
        self.dlg_upload = None

        # dialog
        self.dlg_modality = None

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

    def build_interface(self):
        title = ft.Text("XNAT-PIC Uploader", size=26,
                        weight=ft.FontWeight.BOLD)

        # File picker
        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self._page.overlay.append(self.file_picker)

        # Row 1: level buttons
        self.btn_project = ft.ElevatedButton(
            "Project",
            on_click=self._controller.upload_project,
            expand=True,
        )
        self.btn_subject = ft.ElevatedButton(
            "Subject",
            on_click=self._controller.upload_subject,
            expand=True,
        )
        self.btn_experiment = ft.ElevatedButton(
            "Experiment",
            on_click=self._controller.upload_experiment,
            expand=True,
        )
        self.btn_file = ft.ElevatedButton(
            "File",
            on_click=self._controller.upload_file,
            expand=True,
        )

        row_levels = ft.Row(
            [self.btn_project, self.btn_subject, self.btn_experiment,
             self.btn_file],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=5,
        )

        # Row 2: select folder + tree + preview + show tags + modify modality
        self.btn_select_folder = ft.ElevatedButton(
            "Select folder",
            disabled=True,
            on_click=lambda e: self.file_picker.get_directory_path(),
        )

        self.tree_view_dcm = ft.Container(
            width=220,
            height=260,
            content=ft.ListView([], expand=True, spacing=2),
            border=ft.border.all(1, ft.Colors.YELLOW_200),
            border_radius=5,
            padding=5,
        )

        self.img_preview = ft.Image(
            src="",
            width=220,
            height=220,
            fit=ft.ImageFit.CONTAIN,
        )

        self.btn_show_tags = ft.ElevatedButton(
            "Show DICOM tags",
            disabled=True,
            on_click=self._controller.on_show_tags_clicked,
        )

        self.cnt_modify_modality = ft.Column()
        self.btn_modify_modality = ft.ElevatedButton(
            "Modify DICOM modality",
            disabled=True,
            on_click=self._controller.modify_modality,
        )
        self.dd_modify_modality = ft.Dropdown(
            options=[
                ft.dropdown.Option("MR"),
                ft.dropdown.Option("US"),
                ft.dropdown.Option("OI"),
                ft.dropdown.Option("OA")
            ],
            hint_text="New Modality",
            width=200,
            disabled=False,
            on_change=self._controller.on_select_modality,
        )

        self.cnt_modify_modality.controls.append(self.btn_modify_modality)

        col_preview = ft.Column(
            [self.img_preview, self.btn_show_tags, self.cnt_modify_modality],
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
        )

        row_file = ft.Row(
            [
                self.btn_select_folder,
                self.tree_view_dcm,
                col_preview,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Row 3: dropdowns (project, subject, experiment in xnat)
        self.dd_xnat_project = ft.Dropdown(
            hint_text="Project",
            width=200,
            disabled=True,
            on_change=self._controller.on_project_selected,
        )
        self.dd_xnat_subject = ft.Dropdown(
            hint_text="Subject",
            width=200,
            disabled=True,
            on_change=self._controller.on_subject_selected,
        )
        self.dd_xnat_experiment = ft.Dropdown(
            hint_text="Experiment",
            width=200,
            disabled=True,
        )

        row_dd = ft.Row(
            [self.dd_xnat_project, self.dd_xnat_subject,
             self.dd_xnat_experiment],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Row 4: new project, subject, experiment in xnat
        self.btn_new_project = ft.ElevatedButton(
            "New Project",
            disabled=True,
            on_click=self._controller.create_new_project
        )
        self.btn_new_subject = ft.ElevatedButton("New Subject", disabled=True)
        self.btn_new_experiment = ft.ElevatedButton("New Experiment",
                                                    disabled=True)

        row_new = ft.Row(
            [self.btn_new_project, self.btn_new_subject,
             self.btn_new_experiment],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Row 5: home/back + upload
        self.btn_home_back = ft.ElevatedButton(
            "Home",
            on_click=self._controller.on_home_back_clicked,
        )
        self.btn_upload = ft.ElevatedButton(
            "Upload",
            disabled=True,
            on_click=self._controller.dicom_upload,
        )

        row_bottom = ft.Row(
            [self.btn_home_back, self.btn_upload],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Progress dialog
        self.pb_upload = ft.ProgressBar(width=250)
        self.dlg_upload = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading..."),
            content=self.pb_upload,
        )

        self._main_layout = ft.Column(
            [
                title,
                row_levels,
                row_file,
                row_dd,
                row_new,
                row_bottom,
            ],
            spacing=15,
            expand=True,
        )

        return self._main_layout

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
        self.img_preview.src = ""

        # Modality dropdown reset
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
    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._controller.get_directory_to_upload(e.path)
        else:
            self.create_alert("No folder selected.")

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