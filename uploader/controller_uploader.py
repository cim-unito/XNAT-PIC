from pathlib import Path
import threading
import flet as ft

from enums.tree_type import TreeType
from enums.uploader_level import UploaderLevel
from uploader.services.dicom.dicom_preview_service import DicomPreviewService
from uploader.services.dicom.dicom_tag_reader_service import \
    DicomTagReaderService
from shared_ui.ui.treeview.controller_treeview import ControllerTreeview
from shared_ui.ui.treeview.model_treeview import ModelTreeview
from shared_ui.ui.treeview.view_treeview import ViewTreeview
from xnat_client.xnat_repository import XnatRepository
from uploader.xnat_new_project.model_xnat_new_project import \
    ModelXnatNewProject
from uploader.xnat_new_project.view_xnat_new_project import ViewXnatNewProject
from uploader.xnat_new_project.controller_xnat_new_project import \
    ControllerXnatNewProject

class ControllerUploader:
    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._treeview_model = ModelTreeview()
        self._treeview_view = ViewTreeview(self._view)
        self._treeview_controller = ControllerTreeview(
            self._treeview_model,
            self._treeview_view,
            on_collapse=self._on_treeview_collapse,
            on_expand_selected=self._on_treeview_expand,
            on_file_selected=self._on_treeview_file_selected,
        )
        self._view_xnat_auth = None
        self._controller_xnat_auth = None

        self._model_xnat_new_project = ModelXnatNewProject()
        self._view_xnat_new_project = ViewXnatNewProject(self._view.page,
                                                         on_submit=self.on_data_project_collected)
        self._controller_xnat_new_project = ControllerXnatNewProject(
            self._view_xnat_new_project,
            self._model_xnat_new_project,
        )
        self._view_xnat_new_project.set_controller(
            self._controller_xnat_new_project)

        self._xnat_session = None
        self._xnat_repo = None

        self.file_path_selected = None
        self.folder_path_selected = None
        self.preview_cache = {}

    # ==========================================================
    # LOGIN / ROUTE
    # ==========================================================
    def set_xnat_auth(self, view_auth, controller_auth):
        self._view_xnat_auth = view_auth
        self._controller_xnat_auth = controller_auth

    def on_enter_route(self):
        dlg = self._view_xnat_auth.build_dialog(
            on_success=self._on_login_success,
            on_cancel=self._on_login_cancel,
        )
        self._view.open_auth_dialog(dlg)

    def on_exit_route(self):
        if self._xnat_session:
            self._xnat_session.disconnect()

    def _on_login_success(self, xnat_session):
        self._xnat_session = xnat_session
        self._xnat_repo = XnatRepository(xnat_session)
        self._view.set_initial_state()

    def _on_login_cancel(self):
        if self._xnat_session:
            self._xnat_session.disconnect()
        self.go_home()

    # ==========================================================
    # HOME / BACK
    # ==========================================================
    def go_home(self):
        self._view._page.go("/")

    def on_home_back_clicked(self, e):
        if self._model.level is None:
            self._view.set_initial_state()
            self.go_home()
        else:
            self._model.reset_level()
            self._view.set_initial_state()

    # ==========================================================
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT / FILE)
    # ==========================================================
    def upload_project(self, e):
        """Start a project-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.PROJECT)
        self._view.open_directory_picker()

    def upload_subject(self, e):
        """Start a subject-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.SUBJECT)
        self._view.open_directory_picker()

    def upload_experiment(self, e):
        """Start a experiment-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.EXPERIMENT)
        self._view.open_directory_picker()

    def upload_file(self, e):
        """Start a file-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.FILE)
        self._view.open_directory_picker()

    # ==========================================================
    # DROPDOWN PROJECT / SUBJECT / EXPERIMENT XNAT
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

    # -------------------------------------------------------
    # TREEVIEW DICOM FILES
    # -------------------------------------------------------
    def get_directory_to_upload(self, path: str):
        self._model.input_root = path
        self._model.validate_dicom_files()
        self._treeview_controller.populate_tree(
            self._model.tmp_folder_to_upload,
            TreeType.DICOM)

    # ==========================================================
    # FILE SELECTION + DICOM PREVIEW
    # ==========================================================
    def _on_treeview_file_selected(self, file_path):
        """Handle a file selection in the treeview."""
        self.file_path_selected = file_path
        self.folder_path_selected = None
        print(f"[SELECTED FILE] {self.file_path_selected}")
        p = Path(self.file_path_selected)

        if p in self.preview_cache:
            self._view.set_image_preview(self.preview_cache[p])
            return

        try:
            if p.suffix.lower() in (".dcm", ".dicom"):
                b64 = DicomPreviewService.dicom_to_base64(p)
                self.preview_cache[p] = b64
                self._view.set_image_preview(b64)
        except Exception as e:
            self._view.create_alert(f"Preview failed: {e}")

    def on_show_tags_clicked(self, e):
        if not self.file_path_selected:
            self._view.create_alert("No file selected.")
            return
        try:
            tags = DicomTagReaderService.read_dicom_tags(
                self.file_path_selected)
            self._view.show_dicom_tags_dialog(tags)
        except Exception as e:
            self._view.create_alert(f"Cannot read DICOM tags: {e}")

    # ==========================================================
    # MODIFY MODALITY
    # ==========================================================
    def modify_modality(self, e):
        self._view.cnt_modify_modality.controls.clear()
        self._view.cnt_modify_modality.controls.append(
            self._view.dd_modify_modality)
        self._view.page.update()

    def on_select_modality(self, e):
        if self.folder_path_selected is None and self.file_path_selected is None:
            self._view.create_alert("No file selected.")
            return

        selected_item = self.folder_path_selected if (self.folder_path_selected
                                                      is not None) \
            else self.file_path_selected
        print(selected_item)
        self._model.modify_modality(Path(selected_item),
                                    e.control.value)
        self._treeview_controller.populate_tree(
            Path(self._model.tmp_folder_to_upload),
            TreeType.DICOM
        )
        self.preview_cache.clear()
        self._view.reset_image_preview()
        self._view.dd_modify_modality.value = None
        self._view.cnt_modify_modality.controls.clear()
        self._view.cnt_modify_modality.controls.append(
            self._view.btn_modify_modality)
        self._view.page.update()

    # ==========================================================
    # NEW XNAT PROJECT
    # ==========================================================
    def create_new_project(self, e):
        self._view_xnat_new_project.open()

    def on_data_project_collected(self, data):
        self._xnat_repo.create_project(data)
        project_id = data["project_id"]
        exists = False

        for opt in self._view.dd_xnat_project.options:
            if opt.key == project_id:
                exists = True
                break

        if not exists:
            print("Add new project:", project_id)
            self._view.dd_xnat_project.options.append(
                ft.dropdown.Option(key=project_id, text=project_id)
            )

        self._view.dd_xnat_project.value = project_id
        self._view.dd_xnat_project.update()

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

        base_path = self._model.tmp_folder_to_upload
        if not base_path or not base_path.exists():
            self._view.create_alert("Select a folder to upload.")
            return

        project_id = self._view.dd_xnat_project.value
        if not project_id:
            self._view.create_alert("Select a project in XNAT.")
            return

        self._view.show_progress_bar_dialog()

        # t = threading.Thread(
        #     target=self._upload_project_thread,
        #     args=(base_path, project_id),
        #     daemon=True,
        # )
        # t.start()

        self._upload_project_thread(base_path, project_id)

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
                    return

        # ---- Completed! ----
        self._view.dlg_upload.open = False
        self._view.update_page()
        self._view.create_alert("Upload completed successfully!")

    def _set_level(self, level):
        self._model.level = level
        """Set the uploader level and update the view mode."""
        if level == UploaderLevel.PROJECT:
            self._view.set_mode(xnat_subject=False, xnat_experiment=False)
        elif level == UploaderLevel.SUBJECT:
            self._view.set_mode(xnat_subject=True, xnat_experiment=False)
        elif level == UploaderLevel.EXPERIMENT:
            self._view.set_mode(xnat_subject=True, xnat_experiment=True)
        elif level == UploaderLevel.FILE:
            self._view.set_mode(xnat_subject=True, xnat_experiment=True)

        self.load_projects()

    def _on_treeview_collapse(self, node_path, tile):
        """Handle a treeview node collapse."""
        self.folder_path_selected = None
        self.file_path_selected = None

    def _on_treeview_expand(self, node_path, tile):
        """Handle a treeview node expansion."""
        self.folder_path_selected = node_path
        self.file_path_selected = None

