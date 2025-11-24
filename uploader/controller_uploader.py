from pathlib import Path
import threading

from uploader.utils.dicom_parser import DicomParser
from xnat_client.xnat_repository import XnatRepository
from uploader.xnat_new_project.model_xnat_new_project import ModelXnatNewProject
from uploader.xnat_new_project.view_xnat_new_project import ViewXnatNewProject
from uploader.xnat_new_project.controller_xnat_new_project import ControllerXnatNewProject

class ControllerUploader:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view_xnat_auth = None
        self.__controller_xnat_auth = None

        self._model_xnat_new_project = ModelXnatNewProject()
        self._view_xnat_new_project = ViewXnatNewProject(self._view._page,
                                                         on_submit=self.on_data_project_collected)
        self._controller_xnat_new_project = ControllerXnatNewProject(
            self._view_xnat_new_project,
            self._model_xnat_new_project,
        )
        self._view_xnat_new_project.set_controller(self._controller_xnat_new_project)

        self._xnat_session = None
        self._xnat_repo = None

        self._mode_selected: None
        self.file_path: None
        self.preview_cache = {}

    # ==========================================================
    # LOGIN / ROUTE
    # ==========================================================
    def set_xnat_auth(self, view_auth, controller_auth):
        self._view_xnat_auth = view_auth
        self.__controller_xnat_auth = controller_auth

    def on_enter_route(self):
        self._mode_selected = None
        self._view.disable_all_for_login()

        dlg = self._view_xnat_auth.build_dialog(
            on_success=self._on_login_success,
            on_cancel=self._on_login_cancel,
        )
        self._view.open_auth_dialog(dlg)

    def on_exit_route(self):
        self._xnat_session.disconnect()

    def _on_login_success(self, xnat_session):
        self._xnat_session = xnat_session
        self._xnat_repo = XnatRepository(xnat_session)
        self._view.set_initial_state()

    def _on_login_cancel(self):
        self._xnat_session.disconnect()
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

        self.load_projects()

    # ==========================================================
    # SCELTA LIVELLO (PROJECT / SUBJECT / EXPERIMENT / FILE)
    # ==========================================================
    def upload_project(self, e):
        self._model.level = "project"
        self._set_mode_for_level("project")

    def upload_subject(self, e):
        self._model.level = "subject"
        self._set_mode_for_level("subject")

    def upload_experiment(self, e):
        self._model.level = "experiment"
        self._set_mode_for_level("experiment")

    def upload_file(self, e):
        self._model.level = "file"
        self._set_mode_for_level("file")

    # ==========================================================
    # DROPDOWN XNAT
    # ==========================================================
    def load_projects(self):
        try:
            projects = self._xnat_repo.list_projects()
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
            subjects = self._xnat_repo.list_subjects(project_id)
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
            experiments = self._xnat_repo.list_experiments(project_id,
                                                           subject_id)
            self._view.populate_experiments(experiments)
        except Exception as e:
            self._view.create_alert(f"Cannot load experiments: {e}")

    # ==========================================================
    # FILE SYSTEM / TREEVIEW
    # ==========================================================
    def get_directory_to_upload(self, path: str):
        p = Path(path)
        self._model.path_to_upload = p
        if not self._model.validate_scan():
            upload_path_xnat = p.parent / (p.name + "_xnat")
            self._model.create_xnat_folder(upload_path_xnat)
            self._model.create_new_scan(upload_path_xnat)
            p = upload_path_xnat
            self._model.path_to_upload = upload_path_xnat

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
        self._view.highlight_folder(node_path)
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

        if filepath in self.preview_cache:
            self._view.set_image_preview(self.preview_cache[filepath])
            return

        try:
            if p.suffix.lower() in (".dcm", ".dicom"):
                b64 = DicomParser.dicom_to_base64(p)
                self.preview_cache[filepath] = b64
                self._view.set_image_preview(b64)
        except Exception as e:
            self._view.create_alert(f"Preview failed: {e}")

    def on_show_tags_clicked(self, e):
        if not self.file_path:
            self._view.create_alert("No file selected.")
            return
        try:
            tags = DicomParser.read_DICOM_tags(self.file_path)
            self._view.show_dicom_tags_dialog(tags)
        except Exception as e:
            self._view.create_alert(f"Cannot read DICOM tags: {e}")

    # ==========================================================
    # NEW XNAT PROJECT
    # ==========================================================
    def create_new_project(self, e):
        self._view_xnat_new_project.open()

    def on_data_project_collected(self, data):
        self._xnat_repo.create_project(data)

    # ==========================================================
    # UPLOAD
    # ==========================================================
    def _normalize_id(self, name):
        name = name.strip()
        name = name.replace(" ", "_")
        name = name.replace(".", "_")
        name = name.replace("-", "_")
        return name.upper()

    def dicom_upload(self, e):
        if not self._xnat_repo:
            self._view.create_alert("You must login to XNAT first.")
            return

        base_path = self._model.path_to_upload
        if not base_path or not base_path.exists():
            self._view.create_alert("Select a folder to upload.")
            return
        if not self._model.exist_ot_modality():
            project_id = self._view.dd_xnat_project.value
            if not project_id:
                self._view.create_alert("Select a project in XNAT.")
                return

            self._view.show_progress_dialog()

            t = threading.Thread(
                target=self._upload_project_thread,
                args=(base_path, project_id),
                daemon=True,
            )
            t.start()
        else:
            self._view.show_upload_ot_modality()

    def upload(self):
        base_path = self._model.path_to_upload
        project_id = self._view.dd_xnat_project.value
        if not project_id:
            self._view.create_alert("Select a project in XNAT.")
            return

        self._view.show_progress_dialog()

        t = threading.Thread(
            target=self._upload_project_thread,
            args=(base_path, project_id),
            daemon=True,
        )
        t.start()

    def modify_modality(self, e):
        self._view.cnt_modify_modality.controls.clear()
        self._view.cnt_modify_modality.controls.append(
            self._view.dd_modify_modality)
        self._view._page.update()
        print(self._view.selected_folders)

    def on_select_modality(self, e):
        print("Hai selezionato:", e.control.value)
        print(self._view.selected_folders)

        self._model.modify_modality(self._view.selected_folders, e.control.value)
        p = Path(self._model.path_to_upload)
        self.populate_tree(p)

        self._view.cnt_modify_modality.controls.clear()
        self._view.cnt_modify_modality.controls.append(self._view.btn_modify_modality)
        self._view._page.update()

    def _upload_project_thread(self, base_path: Path, project_id: str):
        subjects = [p for p in base_path.iterdir() if p.is_dir()]

        if not subjects:
            self._view.create_alert(
                "No subject folders found in selected path.")
            return

        total = sum(
            len([e for e in s.iterdir() if e.is_dir()]) for s in subjects)

        if total == 0:
            self._view.create_alert("No experiment folders found.")
            return

        done = 0

        for subj in subjects:

            # SUBJECT ID — dropdown oppure cartella
            if self._view.dd_xnat_subject.value:
                subject_id = self._view.dd_xnat_subject.value
            else:
                subject_id = self._normalize_id(subj.name)

            experiments = [e for e in subj.iterdir() if e.is_dir()]

            for exp_folder in experiments:

                if self._view.dd_xnat_experiment.value:
                    experiment_id = self._view.dd_xnat_experiment.value
                else:
                    experiment_id = self._normalize_id(exp_folder.name)

                try:
                    # CHIAMATA AL REPOSITORY
                    self._xnat_repo.upload_dicom(
                        exp_folder,
                        project_id,
                        subject_id,
                        experiment_id
                    )

                except Exception as err:
                    self._view.create_alert(f"Upload error: {err}")
                    self._view._page.update()
                    return

                # UPDATE PROGRESS (TUO METODO ORIGINALE)
                done += 1
                progress = done / total
                self._view.update_progress(progress)
                self._view._page.update()

        # ---- COMPLETATO ----

        self._view.update_progress(1.0)
        self._view._page.update()

        # chiudi dialog e mostra messaggio finale
        self._view.create_alert("Upload completed successfully!")
        self._view._page.update()