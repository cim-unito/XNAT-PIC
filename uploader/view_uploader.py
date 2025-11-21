import flet as ft
from pathlib import Path


class ViewUploader(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        self._dlg_auth = None
        self.selected_file = None
        self._main_layout = None

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

        # progress
        self.pb_upload = None
        self.dlg_upload = None

    def set_controller(self, controller):
        self._controller = controller

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
        title = ft.Text("XNAT-PIC Uploader", size=26, weight=ft.FontWeight.BOLD)

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
            [self.btn_project, self.btn_subject, self.btn_experiment, self.btn_file],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=5,
        )

        # Row 2: select folder + tree + preview + show tags
        self.btn_select_folder = ft.ElevatedButton(
            "Select folder",
            disabled=True,
            on_click=lambda e: self.file_picker.get_directory_path(),
        )

        self.tree_view_dcm = ft.Container(
            width=220,
            height=260,
            content=ft.ListView([], expand=True, spacing=2),
            border=ft.border.all(1, ft.Colors.GREY_400),
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

        col_preview = ft.Column(
            [self.img_preview, self.btn_show_tags],
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

        # Row 3: dropdowns
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
            [self.dd_xnat_project, self.dd_xnat_subject, self.dd_xnat_experiment],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Row 4: new buttons
        self.btn_new_project = ft.ElevatedButton(
            "New Project",
            disabled=True,
            on_click=self._controller.create_new_project
        )
        self.btn_new_subject = ft.ElevatedButton("New Subject", disabled=True)
        self.btn_new_experiment = ft.ElevatedButton("New Experiment", disabled=True)

        row_new = ft.Row(
            [self.btn_new_project, self.btn_new_subject, self.btn_new_experiment],
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
            title=ft.Text("Uploading..."),
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
    # STATO INIZIALE / DISABLE
    # ------------------------------------------------------
    def disable_all_for_login(self):
        # tutto disabilitato durante il login
        all_ctrls = [
            self.btn_project, self.btn_subject, self.btn_experiment, self.btn_file,
            self.btn_select_folder,
            self.btn_show_tags,
            self.dd_xnat_project, self.dd_xnat_subject, self.dd_xnat_experiment,
            self.btn_new_project, self.btn_new_subject, self.btn_new_experiment,
            self.btn_upload,
        ]
        for c in all_ctrls:
            if c:
                c.disabled = True

        if self.btn_home_back:
            self.btn_home_back.disabled = True

        self._page.update()

    def set_initial_state(self):
        """
        Stato iniziale dopo login:
        - abilitati solo i 4 pulsanti Project/Subject/Experiment/File
        - il resto disabilitato
        - Home attivo
        """
        if self.btn_project:
            self.btn_project.disabled = False
        if self.btn_subject:
            self.btn_subject.disabled = False
        if self.btn_experiment:
            self.btn_experiment.disabled = False
        if self.btn_file:
            self.btn_file.disabled = False

        for c in [
            self.btn_select_folder,
            self.btn_show_tags,
            self.dd_xnat_project,
            self.dd_xnat_subject,
            self.dd_xnat_experiment,
            self.btn_new_project,
            self.btn_new_subject,
            self.btn_new_experiment,
            self.btn_upload,
        ]:
            if c:
                c.disabled = True

        if self.btn_home_back:
            self.btn_home_back.text = "Home"
            self.btn_home_back.disabled = False

        # reset dropdown
        if self.dd_xnat_project:
            self.dd_xnat_project.value = None
            self.dd_xnat_project.options = []
        if self.dd_xnat_subject:
            self.dd_xnat_subject.value = None
            self.dd_xnat_subject.options = []
        if self.dd_xnat_experiment:
            self.dd_xnat_experiment.value = None
            self.dd_xnat_experiment.options = []

        self._page.update()

    # ------------------------------------------------------
    # MODALITÀ LIVELLO
    # ------------------------------------------------------
    def set_mode(
        self,
        level_buttons_enabled: bool,
        select_group_enabled: bool,
        upload_enabled: bool,
        dd_project: bool,
        dd_subject: bool,
        dd_experiment: bool,
        new_project: bool,
        new_subject: bool,
        new_experiment: bool,
    ):
        # abilita/disabilita pulsanti di livello
        for c in [
            self.btn_project,
            self.btn_subject,
            self.btn_experiment,
            self.btn_file,
        ]:
            if c:
                c.disabled = not level_buttons_enabled

        # select folder / tree / preview / show tags viaggiano insieme
        for c in [
            self.btn_select_folder,
            self.btn_show_tags,
        ]:
            if c:
                c.disabled = not select_group_enabled

        # dropdown
        if self.dd_xnat_project:
            self.dd_xnat_project.disabled = not dd_project
        if self.dd_xnat_subject:
            self.dd_xnat_subject.disabled = not dd_subject
        if self.dd_xnat_experiment:
            self.dd_xnat_experiment.disabled = not dd_experiment

        # new buttons
        if self.btn_new_project:
            self.btn_new_project.disabled = not new_project
        if self.btn_new_subject:
            self.btn_new_subject.disabled = not new_subject
        if self.btn_new_experiment:
            self.btn_new_experiment.disabled = not new_experiment

        # upload
        if self.btn_upload:
            self.btn_upload.disabled = not upload_enabled

        # home/back
        if self.btn_home_back:
            self.btn_home_back.text = "Back"

        self._page.update()

    # ------------------------------------------------------
    # POPOLAMENTO DROPDOWN
    # ------------------------------------------------------
    def populate_projects(self, projects):
        self.dd_xnat_project.options = [
            ft.dropdown.Option(key=p["id"], text=p["label"]) for p in projects
        ]
        self.dd_xnat_project.value = None
        self.dd_xnat_subject.options = []
        self.dd_xnat_subject.value = None
        self.dd_xnat_experiment.options = []
        self.dd_xnat_experiment.value = None
        self._page.update()

    def populate_subjects(self, subjects):
        self.dd_xnat_subject.options = [
            ft.dropdown.Option(key=s["id"], text=s["label"]) for s in subjects
        ]
        self.dd_xnat_subject.value = None
        self.dd_xnat_experiment.options = []
        self.dd_xnat_experiment.value = None
        self._page.update()

    def populate_experiments(self, experiments):
        self.dd_xnat_experiment.options = [
            ft.dropdown.Option(key=e["id"], text=e["label"]) for e in experiments
        ]
        self.dd_xnat_experiment.value = None
        self._page.update()

    # ------------------------------------------------------
    # FILE PICKER & TREE
    # ------------------------------------------------------
    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._controller.get_directory_to_upload(e.path)
        else:
            self.create_alert("No folder selected.")

    def build_lazy_tree(self, items, expand_callback, file_selected_callback):
        tiles = []
        for it in items:
            if it["is_dir"]:
                tiles.append(self.make_lazy_folder(it, expand_callback))
            else:
                tiles.append(self.make_file_tile(it, file_selected_callback))
        return ft.ListView(tiles, expand=True, spacing=2)

    def make_lazy_folder(self, item, expand_callback):
        return ft.ExpansionTile(
            title=ft.Text(item["name"]),
            leading=ft.Icon(ft.Icons.FOLDER),
            controls=[ft.Text("Loading...")],
            on_change=lambda e, p=item["path"]: expand_callback(e, p, e.control),
        )

    def make_file_tile(self, item, file_selected_callback):
        bgcolor = (
            ft.Colors.BLUE_100
            if self.selected_file == item["path"]
            else ft.Colors.WHITE
        )
        return ft.ListTile(
            title=ft.Text(item["name"]),
            leading=ft.Icon(ft.Icons.DESCRIPTION),
            bgcolor=bgcolor,
            on_click=lambda e, p=item["path"]: file_selected_callback(p),
        )

    def update_tree(self, tree_widget):
        self.tree_view_dcm.content = tree_widget
        self._page.update()

    def highlight_selected_file(self, filepath: str):
        self.selected_file = filepath
        # for simplicity, ricostruzione grafica demandata a update_tree
        self._page.update()

    # ------------------------------------------------------
    # IMMAGINE & DICOM TAGS
    # ------------------------------------------------------
    def set_image_preview(self, b64: str):
        self.img_preview.src_base64 = b64
        self.img_preview.update()

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
            actions=[ft.TextButton("Close", on_click=lambda e: self._page.close(dlg))],
            modal=True,
        )
        self._page.open(dlg)
        self._page.update()

    # ------------------------------------------------------
    # PROGRESS / ALERT
    # ------------------------------------------------------
    def show_progress_dialog(self):
        self._page.open(self.dlg_upload)
        self._page.update()

    def update_progress(self, value: float):
        self.pb_upload.value = value
        self._page.update()

    def create_alert(self, message: str):
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