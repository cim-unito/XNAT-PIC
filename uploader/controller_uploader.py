from pathlib import Path
import threading

from xnat_client.xnat_manager import XnatManager


class ControllerUploader:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._xnat_auth_view = None
        self._xnat_auth_controller = None

        self._new_project_view = None
        self._new_project_controller = None

        self._mode_selected: str | None = None
        self.file_path: Path | None = None
        self.preview_cache: dict[str, str] = {}

    # ==========================================================
    # LOGIN / ROUTE
    # ==========================================================
    def set_xnat_auth(self, view_auth, controller_auth):
        self._xnat_auth_view = view_auth
        self._xnat_auth_controller = controller_auth

    def on_enter_route(self):
        # logout XNAT
        XnatManager.disconnect_global()
        self._mode_selected = None

        self._view.disable_all_for_login()

        dlg = self._xnat_auth_view.build_dialog(
            on_success=self._on_login_success,
            on_cancel=self._on_login_cancel,
        )
        self._view.open_auth_dialog(dlg)

    def on_exit_route(self):
        XnatManager.disconnect_global()
        self._view.close_auth_dialog()

    def _on_login_success(self):
        self._view.close_auth_dialog()
        self._view.set_initial_state()

    def _on_login_cancel(self):
        self._view.close_auth_dialog()
        self.go_home()

    # ==========================================================
    # NAVIGAZIONE
    # ==========================================================
    def go_home(self):
        self._view._page.go("/")

    def on_home_back_clicked(self, e):
        if self._mode_selected is None:
            self.go_home()
        else:
            self._mode_selected = None
            self._view.set_initial_state()

    # ==========================================================
    # UTIL PER IMPOSTARE MODALITÀ LIVELLO
    # ==========================================================
    def _set_mode_for_level(self, mode: str):
        """
        Centralizza le combinazioni di flag per i vari livelli.

        ATTENZIONE: qui manteniamo ESATTAMENTE la stessa configurazione
        che avevi nei singoli metodi upload_project/subject/experiment/file.
        """
        self._mode_selected = mode

        if mode == "project":
            self._view.set_mode(
                level_buttons_enabled=False,
                select_group_enabled=True,
                upload_enabled=True,
                dd_project=True,
                dd_subject=False,
                dd_experiment=False,
                new_project=True,
                new_subject=False,
                new_experiment=False,
            )
        elif mode == "subject":
            self._view.set_mode(
                level_buttons_enabled=False,
                select_group_enabled=True,
                upload_enabled=True,
                dd_project=True,
                dd_subject=True,
                dd_experiment=False,
                new_project=True,
                new_subject=True,
                new_experiment=False,
            )
        elif mode == "experiment":
            self._view.set_mode(
                level_buttons_enabled=False,
                select_group_enabled=True,
                upload_enabled=True,
                dd_project=True,
                dd_subject=True,
                dd_experiment=True,
                new_project=True,
                new_subject=True,
                new_experiment=True,
            )
        elif mode == "file":
            # identico a experiment
            self._view.set_mode(
                level_buttons_enabled=False,
                select_group_enabled=True,
                upload_enabled=True,
                dd_project=True,
                dd_subject=True,
                dd_experiment=True,
                new_project=True,
                new_subject=True,
                new_experiment=True,
            )
        else:
            raise ValueError(f"Unknown upload mode: {mode}")

        # load projects rimane identico
        self.load_projects()

    # ==========================================================
    # SCELTA LIVELLO (PROJECT / SUBJECT / EXPERIMENT / FILE)
    # ==========================================================
    def upload_project(self, e):
        self._set_mode_for_level("project")

    def upload_subject(self, e):
        self._set_mode_for_level("subject")

    def upload_experiment(self, e):
        self._set_mode_for_level("experiment")

    def upload_file(self, e):
        self._set_mode_for_level("file")

    # ==========================================================
    # DROPDOWN XNAT
    # ==========================================================
    def load_projects(self):
        try:
            projects = XnatManager.list_projects()
            self._view.populate_projects(projects)
        except Exception as e:
            self._view.create_alert(f"Cannot load projects: {e}")

    def on_project_selected(self, e):
        project_id = self._view.dd_xnat_project.value
        self._view.populate_subjects([])
        self._view.populate_experiments([])

        if not project_id:
            return

        try:
            subjects = XnatManager.list_subjects(project_id)
            self._view.populate_subjects(subjects)
        except Exception as e:
            self._view.create_alert(f"Cannot load subjects: {e}")

    def on_subject_selected(self, e):
        project_id = self._view.dd_xnat_project.value
        subject_id = self._view.dd_xnat_subject.value
        self._view.populate_experiments([])

        if not project_id or not subject_id:
            return

        try:
            experiments = XnatManager.list_experiments(project_id, subject_id)
            self._view.populate_experiments(experiments)
        except Exception as e:
            self._view.create_alert(f"Cannot load experiments: {e}")

    # ==========================================================
    # FILE SYSTEM / TREEVIEW
    # ==========================================================
    def get_directory_to_upload(self, path: str):
        p = Path(path)
        self._model.path_to_upload = p
        self.populate_tree(p)

    def populate_tree(self, path: Path):
        try:
            items = self._model.list_directory(path)
            tree_widget = self._view.build_lazy_tree(
                items,
                expand_callback=self.on_expand,
                file_selected_callback=self.on_file_selected,
            )
            self._view.update_tree(tree_widget)
        except Exception as e:
            self._view.create_alert(f"Error reading directory: {e}")

    def on_expand(self, e, node_path: str, tile):
        try:
            items = self._model.list_directory(Path(node_path))
            tile.controls.clear()
            for it in items:
                if it["is_dir"]:
                    tile.controls.append(
                        self._view.make_lazy_folder(it, self.on_expand)
                    )
                else:
                    tile.controls.append(
                        self._view.make_file_tile(it, self.on_file_selected)
                    )
            self._view.update_page()
        except Exception as e:
            self._view.create_alert(f"Cannot expand folder: {e}")

    # ==========================================================
    # FILE SELECTION + DICOM PREVIEW
    # ==========================================================
    def on_file_selected(self, filepath: str):
        p = Path(filepath)
        self.file_path = p
        self._view.highlight_selected_file(filepath)

        # cache
        if filepath in self.preview_cache:
            self._view.set_image_preview(self.preview_cache[filepath])
            return

        try:
            if p.suffix.lower() in (".dcm", ".dicom"):
                b64 = self._model.dicom_to_base64(p)
                self.preview_cache[filepath] = b64
                self._view.set_image_preview(b64)
        except Exception as e:
            self._view.create_alert(f"Preview failed: {e}")

    def on_show_tags_clicked(self, e):
        if not self.file_path:
            self._view.create_alert("No file selected.")
            return
        try:
            tags = self._model.read_dicom_tags(self.file_path)
            self._view.show_dicom_tags_dialog(tags)
        except Exception as e:
            self._view.create_alert(f"Cannot read DICOM tags: {e}")

    # ==========================================================
    # NEW XNAT PROJECT
    # ==========================================================
    def set_new_project_module(self, view_new_project, controller_new_project):
        self._new_project_view = view_new_project
        self._new_project_controller = controller_new_project

    def create_new_project(self, e=None):
        """
        Gestore click su 'New Project' nell'uploader.
        Apre la dialog 'New XNAT Project'.
        """
        if not self._new_project_view or not self._new_project_controller:
            self._view.create_alert("New project module not configured.")
            return

        def on_created(project_id: str, label: str):
            # Dopo creazione, ricarico lista progetti e seleziono il nuovo.
            try:
                projects = XnatManager.list_projects()
                self._view.populate_projects(projects)
                # seleziona il nuovo progetto
                self._view.dd_xnat_project.value = project_id
                self._view.update_page()
            except Exception as err:
                self._view.create_alert(
                    f"Project created, but cannot refresh list: {err}"
                )

        dlg = self._new_project_view.build_dialog(on_created=on_created)
        self._view._page.open(dlg)
        self._view._page.update()

    # ==========================================================
    # UPLOAD
    # ==========================================================
    def dicom_upload(self, e):
        if not XnatManager.has_active_session():
            self._view.create_alert("You must login to XNAT first.")
            return

        base_path: Path | None = self._model.path_to_upload
        if not base_path or not base_path.exists():
            self._view.create_alert("Select a folder to upload.")
            return

        project_id = self._view.dd_xnat_project.value
        if not project_id:
            self._view.create_alert("Select a project in XNAT.")
            return

        # mostra dialog
        self._view.show_progress_dialog()

        # thread per non bloccare la UI
        t = threading.Thread(
            target=self._upload_project_thread,
            args=(base_path, project_id),
            daemon=True,
        )
        t.start()

    def _upload_project_thread(self, base_path: Path, project_id: str):
        # La logica qui sotto è la stessa del tuo codice originale
        subjects = [p for p in base_path.iterdir() if p.is_dir()]
        if not subjects:
            self._view.create_alert("No subject folders found in selected path.")
            return

        total = 0
        for subj in subjects:
            exps = [e for e in subj.iterdir() if e.is_dir()]
            total += len(exps)

        if total == 0:
            self._view.create_alert("No experiment folders found.")
            return

        done = 0

        for subj in subjects:
            subject_id = subj.name.replace(".", "_")

            experiments = [e for e in subj.iterdir() if e.is_dir()]
            for exp_folder in experiments:
                # experiment_id: base_project _ subject _ experiment
                experiment_id = "_".join(
                    [
                        base_path.name.replace("_dcm", ""),
                        subj.name.replace(".", "_"),
                        exp_folder.name.replace(".", "_"),
                    ]
                ).replace(" ", "_")

                try:
                    self._model.upload_experiment(
                        exp_folder,
                        project_id,
                        subject_id,
                        experiment_id,
                    )
                except Exception as err:
                    self._view.create_alert(str(err))
                    return

                done += 1
                self._view.update_progress(done / total)

        self._view.update_progress(1.0)
