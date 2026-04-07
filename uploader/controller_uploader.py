from pathlib import Path
import flet as ft

from enums.tree_type import TreeType
from enums.uploader_level import UploaderLevel
from shared_ui.ui.xnat_new_subject.controller_xnat_new_subject import ControllerXnatNewSubject
from shared_ui.ui.xnat_new_subject.model_xnat_new_subject import ModelXnatNewSubject
from shared_ui.ui.xnat_new_subject.view_xnat_new_subject import ViewXnatNewSubject
from uploader.services.dicom.dicom_preview_service import DicomPreviewService
from uploader.services.dicom.dicom_tag_reader_service import \
    DicomTagReaderService
from shared_ui.ui.treeview.controller_treeview import ControllerTreeview
from shared_ui.ui.treeview.model_treeview import ModelTreeview
from shared_ui.ui.treeview.view_treeview import ViewTreeview
from xnat_client.xnat_repository import XnatRepository
from shared_ui.ui.xnat_new_project.model_xnat_new_project import \
    ModelXnatNewProject
from shared_ui.ui.xnat_new_project.view_xnat_new_project import ViewXnatNewProject
from shared_ui.ui.xnat_new_project.controller_xnat_new_project import \
    ControllerXnatNewProject
from shared_ui.ui.xnat_new_experiment.model_xnat_new_experiment import \
    ModelXnatNewExperiment
from shared_ui.ui.xnat_new_experiment.view_xnat_new_experiment import \
    ViewXnatNewExperiment
from shared_ui.ui.xnat_new_experiment.controller_xnat_new_experiment import \
    ControllerXnatNewExperiment

class ControllerUploader:
    def __init__(self, view, model):

        self._view = view
        self._model = model

        # Treeview
        self._treeview_model = ModelTreeview()
        self._treeview_view = ViewTreeview(self._view)
        self._treeview_controller = ControllerTreeview(
            self._treeview_model,
            self._treeview_view,
            on_collapse=self._on_treeview_collapse,
            on_expand_selected=self._on_treeview_expand,
            on_file_selected=self._on_treeview_file_selected,
        )

        # Xnat Auth
        self._view_xnat_auth = None
        self._controller_xnat_auth = None

        # New project
        self._model_xnat_new_project = ModelXnatNewProject()
        self._view_xnat_new_project = ViewXnatNewProject(self._view.page)
        self._controller_xnat_new_project = ControllerXnatNewProject(
            self._view_xnat_new_project,
            self._model_xnat_new_project,
            on_submit=self.on_data_project_collected,
        )
        self._view_xnat_new_project.set_controller(
            self._controller_xnat_new_project)

        # New subject
        self._model_xnat_new_subject = ModelXnatNewSubject()
        self._view_xnat_new_subject = ViewXnatNewSubject(self._view.page)
        self._controller_xnat_new_subject = ControllerXnatNewSubject(
            self._view_xnat_new_subject,
            self._model_xnat_new_subject,
            on_submit=self.on_data_subject_collected,
        )
        self._view_xnat_new_subject.set_controller(
            self._controller_xnat_new_subject)

        # New experiment
        self._model_xnat_new_experiment = ModelXnatNewExperiment()
        self._view_xnat_new_experiment = ViewXnatNewExperiment(self._view.page)
        self._controller_xnat_new_experiment = ControllerXnatNewExperiment(
            self._view_xnat_new_experiment,
            self._model_xnat_new_experiment,
            on_submit=self.on_data_experiment_collected,
        )
        self._view_xnat_new_experiment.set_controller(
            self._controller_xnat_new_experiment)
        self._view_xnat_new_experiment.dd_project.on_change = (
            self.on_new_experiment_project_selected
        )

        self._xnat_session = None
        self._xnat_repo = None

        self._selected_file_path = None
        self._selected_folder_path = None
        self._preview_cache = {}

    @property
    def preview_cache(self):
        """Temporary compatibility accessor for the view layer."""
        return self._preview_cache

    # ==========================================================
    # XNAT LOGIN
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
        self._reset_workflow_state()
        if self._xnat_session:
            self._xnat_session.disconnect()
        self._xnat_session = None
        self._xnat_repo = None

    def _on_login_success(self, xnat_session):
        self._xnat_session = xnat_session
        self._xnat_repo = XnatRepository(xnat_session)
        self._view.set_initial_state()

    def _on_login_cancel(self):
        if self._xnat_session:
            self._xnat_session.disconnect()
        self._xnat_session = None
        self._xnat_repo = None
        self.go_home()

    # ==========================================================
    # HOME / BACK
    # ==========================================================
    def go_home(self):
        self._view.page.go("/")

    def on_home_back_clicked(self, e):
        if self._model.level is None:
            self._reset_workflow_state()
            self.go_home()
        else:
            self._reset_workflow_state()

    def _reset_workflow_state(self):
        """Reset uploader workflow state across model, controller, and view."""
        self._model.reset_state()
        self._selected_file_path = None
        self._selected_folder_path = None
        self._preview_cache.clear()
        self._reset_nested_components_state()
        if self._view.dlg_upload:
            self._view.dlg_upload.open = False
        self._view.set_initial_state()

    def _reset_nested_components_state(self):
        """Reset reusable nested components without recreating instances."""
        self._treeview_view.reset_selection()
        self._controller_xnat_new_project.reset_form()
        self._controller_xnat_new_subject.reset_form()
        self._controller_xnat_new_experiment.reset_form()

    # ==========================================================
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT / FILE)
    # ==========================================================
    def upload_project(self, e: ft.ControlEvent):
        """Start a project-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.PROJECT)
        self._view.open_directory_picker()

    def upload_subject(self, e: ft.ControlEvent):
        """Start a subject-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.SUBJECT)
        self._view.open_directory_picker()

    def upload_experiment(self, e: ft.ControlEvent):
        """Start an experiment-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.EXPERIMENT)
        self._view.open_directory_picker()

    def upload_file(self, e: ft.ControlEvent):
        """Start a file-level uploader and open the directory picker."""
        self._set_level(UploaderLevel.FILE)
        self._view.open_directory_picker()

    # ==========================================================
    # DROPDOWN PROJECT / SUBJECT / EXPERIMENT IN XNAT
    # ==========================================================
    def load_projects(self):
        try:
            projects = self._xnat_repo.list_projects()
            self._view.populate_projects(projects)
        except Exception as e:
            self._view.create_alert(f"Cannot load projects: {e}")
            return

    def on_project_selected(self, e: ft.ControlEvent):
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

    def on_subject_selected(self, e: ft.ControlEvent):
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
        try:
            self._model.input_root = path
            list_dicom_files = self._model.get_dicom_files()
            validation_report = self._model.validate_dicom_files(list_dicom_files)
        except (ValueError, RuntimeError, OSError) as e:
            self._view.create_alert(f"Cannot load the {self._model.level}: {e}")
            self._reset_workflow_state()
            return
        except Exception as e:
            self._view.create_alert(
                f"Unexpected error while preparing {self._model.level}: {e}"
            )
            self._reset_workflow_state()
            return

        if validation_report["failed"]:
            failed_preview = "\n".join(
                f"- {Path(entry['file']).name}: {entry['reason']}"
                for entry in validation_report["failed"][:3]
            )
            suffix = "\n..." if len(validation_report["failed"]) > 3 else ""
            self._view.create_alert(
                "Best effort upload prepared. "
                f"Successful: {validation_report['copied'] + validation_report['converted']}, "
                f"failed: {len(validation_report['failed'])}."
                f"\nFirst failures:\n{failed_preview}{suffix}"
            )

        try:
            self._treeview_controller.populate_tree(
                self._model.tmp_folder_to_upload,
                TreeType.DICOM)
        except (ValueError, RuntimeError, OSError) as e:
            self._view.create_alert(f"Cannot show upload tree: {e}")
            self._reset_workflow_state()

    # ==========================================================
    # SHOW DICOM TAGS
    # ==========================================================
    def on_show_tags_clicked(self, e: ft.ControlEvent):
        if not self._selected_file_path:
            self._view.create_alert("No file selected.")
            return
        try:
            tags = DicomTagReaderService.read_dicom_tags(
                self._selected_file_path)
            self._view.show_dicom_tags_dialog(tags)
        except Exception as e:
            self._view.create_alert(f"Cannot read DICOM tags: {e}")

    # ==========================================================
    # MODIFY MODALITY
    # ==========================================================
    def modify_modality(self, e: ft.ControlEvent):
        self._view.cnt_modify_modality.controls.clear()
        self._view.cnt_modify_modality.controls.append(
            self._view.dd_modify_modality)
        self._view.page.update()

    def on_select_modality(self, e: ft.ControlEvent):
        if self._selected_folder_path is None and self._selected_file_path is None:
            self._view.create_alert("No file selected.")
            return

        selected_item = self._selected_folder_path if (self._selected_folder_path
                                                      is not None) \
            else self._selected_file_path
        print(selected_item)
        self._model.modify_modality(Path(selected_item),
                                    e.control.value)
        self._treeview_controller.populate_tree(
            Path(self._model.tmp_folder_to_upload),
            TreeType.DICOM
        )
        self._preview_cache.clear()
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
        self._controller_xnat_new_project.reset_form()
        self._view_xnat_new_project.open()

    def on_data_project_collected(self, data):
        try:
            created_project = self._xnat_repo.create_project(data)
        except Exception as ex:
            self._view.create_alert(f"Cannot create project: {ex}")
            return

        project_id = created_project["project_id"]
        project_label = created_project["project_name"] or project_id
        exists = False

        for opt in self._view.dd_xnat_project.options:
            if opt.key == project_id:
                exists = True
                break

        if not exists:
            print("Add new project:", project_id)
            self._view.dd_xnat_project.options.append(
                ft.dropdown.Option(key=project_id, text=project_label)
            )

        self._view.dd_xnat_project.value = project_id
        self._view.dd_xnat_project.update()

    # ==========================================================
    # NEW XNAT SUBJECT
    # ==========================================================
    def create_new_subject(self, e):
        if not self._xnat_repo:
            self._view.create_alert("You must login to XNAT first.")
            return

        try:
            projects = self._xnat_repo.list_projects()
            project_ids = [project["id"] for project in projects]
            self._view_xnat_new_subject.set_project_options(project_ids)
        except Exception as ex:
            self._view.create_alert(f"Cannot load projects for new subject: {ex}")
            return

        self._controller_xnat_new_subject.reset_form()
        self._view_xnat_new_subject.open()

    def on_data_subject_collected(self, data):
        self._xnat_repo.create_subject(data)
        project_id = data["parent_project"]
        subject_id = data["subject_id"]
        subject_label = data.get("subject_name") or subject_id
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
        try:
            subjects = self._xnat_repo.list_subjects(project_id)
            self._view.populate_subjects(subjects)
        except Exception as ex:
            self._view.create_alert(
                f"Subject created but list refresh failed: {ex}")
            self._view.dd_xnat_project.update()
            return

        subject_exists = any(
            opt.key == subject_id for opt in self._view.dd_xnat_subject.options
        )

        if not subject_exists:
            self._view.dd_xnat_subject.options.append(
                ft.dropdown.Option(key=subject_id, text=subject_label)
            )

        self._view.dd_xnat_subject.value = subject_id
        self._view.dd_xnat_project.update()

    # ==========================================================
    # NEW XNAT EXPERIMENT
    # ==========================================================
    def create_new_experiment(self, e):
        if not self._xnat_repo:
            self._view.create_alert("You must login to XNAT first.")
            return

        try:
            projects = self._xnat_repo.list_projects()
            project_ids = [project["id"] for project in projects]
            self._view_xnat_new_experiment.set_project_options(project_ids)
        except Exception as ex:
            self._view.create_alert(f"Cannot load projects for new subject: {ex}")
            return

        selected_project_id = self._view.dd_xnat_project.value
        self._controller_xnat_new_experiment.reset_form()

        if selected_project_id:
            self._view_xnat_new_experiment.dd_project.value = selected_project_id
            try:
                subjects = self._xnat_repo.list_subjects(selected_project_id)
                self._view_xnat_new_experiment.set_subject_options(subjects)
            except Exception as ex:
                self._view.create_alert(
                    f"Cannot load subjects for project '{selected_project_id}': {ex}")
                return

        self._view_xnat_new_experiment.open()

    def on_new_experiment_project_selected(self, e):
        project_id = self._view_xnat_new_experiment.dd_project.value
        self._view_xnat_new_experiment.set_subject_options([])

        if not project_id:
            self._controller_xnat_new_experiment._update_submit()
            return

        try:
            subjects = self._xnat_repo.list_subjects(project_id)
            self._view_xnat_new_experiment.set_subject_options(subjects)
        except Exception as ex:
            self._view.create_alert(
                f"Cannot load subjects for project '{project_id}': {ex}")

        self._controller_xnat_new_experiment._update_submit()

    def on_data_experiment_collected(self, data):
        self._xnat_repo.create_experiment(data)
        project_id = data["parent_project"]
        subject_id = data["subject_project"]
        experiment_id = data["experiment_id"]
        experiment_label = data.get("experiment_name") or experiment_id
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
        try:
            subjects = self._xnat_repo.list_subjects(project_id)
            self._view.populate_subjects(subjects)
        except Exception as ex:
            self._view.create_alert(
                f"Experiment created but subject list refresh failed: {ex}")
            self._view.dd_xnat_project.update()
            return

        subject_exists = any(
            opt.key == subject_id for opt in self._view.dd_xnat_subject.options
        )

        if not subject_exists:
            self._view.dd_xnat_subject.options.append(
                ft.dropdown.Option(key=subject_id, text=subject_id)
            )

        self._view.dd_xnat_subject.value = subject_id
        try:
            experiments = self._xnat_repo.list_experiments(project_id,
                                                           subject_id)
            self._view.populate_experiments(experiments)
        except Exception as ex:
            self._view.create_alert(
                f"Experiment created but experiment list refresh failed: {ex}")
            self._view.dd_xnat_project.update()
            return

        experiment_exists = any(
            opt.key == experiment_id
            for opt in self._view.dd_xnat_experiment.options
        )

        if not experiment_exists:
            self._view.dd_xnat_experiment.options.append(
                ft.dropdown.Option(key=experiment_id, text=experiment_label)
            )

        self._view.dd_xnat_experiment.value = experiment_id
        self._view.dd_xnat_project.update()


    # ==========================================================
    # UPLOAD
    # ==========================================================
    def _normalize_id(self, name):
        name = name.strip()
        name = name.replace(" ", "_")
        name = name.replace(".", "_")
        name = name.replace("-", "_")
        return name

    def _selected_or_normalized(self, selected_value, fallback_name):
        if selected_value:
            return selected_value
        return self._normalize_id(fallback_name)

    def _iter_upload_targets(self, base_path: Path):
        level = self._model.level

        if level == UploaderLevel.PROJECT:
            subjects = [p for p in base_path.iterdir() if p.is_dir()]
            if not subjects:
                raise ValueError("No subject folders found in selected path.")

            for subj_folder in subjects:
                subject_id = self._selected_or_normalized(
                    self._view.dd_xnat_subject.value,
                    subj_folder.name,
                )
                experiments = [e for e in subj_folder.iterdir() if e.is_dir()]
                for exp_folder in experiments:
                    experiment_id = self._selected_or_normalized(
                        self._view.dd_xnat_experiment.value,
                        exp_folder.name,
                    )
                    yield exp_folder, subject_id, experiment_id

        elif level == UploaderLevel.SUBJECT:
            subject_id = self._selected_or_normalized(
                self._view.dd_xnat_subject.value,
                base_path.name,
            )
            experiments = [e for e in base_path.iterdir() if e.is_dir()]
            for exp_folder in experiments:
                experiment_id = self._selected_or_normalized(
                    self._view.dd_xnat_experiment.value,
                    exp_folder.name,
                )
                yield exp_folder, subject_id, experiment_id

        elif level == UploaderLevel.EXPERIMENT:
            source_experiment = self._model.input_root
            source_subject_name = source_experiment.parent.name

            subject_id = self._selected_or_normalized(
                self._view.dd_xnat_subject.value,
                source_subject_name,
            )
            experiment_id = self._selected_or_normalized(
                self._view.dd_xnat_experiment.value,
                base_path.name,
            )
            yield base_path, subject_id, experiment_id

        else:
            raise ValueError("Selected upload level is not supported.")

    def _validate_experiment_resource_upload_context(self):
        if self._model.level != UploaderLevel.FILE:
            return

        if not self._view.dd_xnat_subject.value:
            raise ValueError(
                "Select an XNAT subject before uploading resources."
            )

        if not self._view.dd_xnat_experiment.value:
            raise ValueError(
                "Select an XNAT experiment before uploading resources."
            )

    def _upload_file_resources_thread(self, base_path: Path, project_id: str):
        subject_id = self._view.dd_xnat_subject.value
        experiment_id = self._view.dd_xnat_experiment.value

        uploaded_files = self._xnat_repo.upload_experiment_resources(
            source_folder=base_path,
            project_id=project_id,
            subject_id=subject_id,
            experiment_id=experiment_id,
        )

        self._view.dlg_upload.open = False
        self._view.update_page()
        self._view.create_alert(
            f"Resources upload completed successfully ({uploaded_files} files)."
        )

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

        try:
            self._validate_experiment_resource_upload_context()
        except ValueError as err:
            self._view.create_alert(str(err))
            return

        # t = threading.Thread(
        #     target=self._upload_project_thread,
        #     args=(base_path, project_id),
        #     daemon=True,
        # )
        # t.start()

        try:
            if self._model.level == UploaderLevel.FILE:
                self._upload_file_resources_thread(base_path, project_id)
            else:
                self._upload_project_thread(base_path, project_id)
        except Exception as err:
            self._view.dlg_upload.open = False
            self._view.update_page()
            self._view.create_alert(f"Upload error: {err}")

    def _upload_project_thread(self, base_path: Path, project_id: str):
        try:
            upload_targets = list(self._iter_upload_targets(base_path))
        except ValueError as err:
            self._view.create_alert(str(err))
            return

        if not upload_targets:
            self._view.create_alert("No experiment folders found.")
            return

        for exp_folder, subject_id, experiment_id in upload_targets:
            try:
                self._xnat_repo.upload_dicom(
                    exp_folder,
                    project_id,
                    subject_id,
                    experiment_id,
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
        self._selected_folder_path = None
        self._selected_file_path = None

    def _on_treeview_expand(self, node_path, tile):
        """Handle a treeview node expansion."""
        self._selected_folder_path = node_path
        self._selected_file_path = None

    def _on_treeview_file_selected(self, file_path):
        """Handle a file selection in the treeview."""
        self._selected_file_path = file_path
        self._selected_folder_path = None
        self._show_selected_file_preview()

    def _show_selected_file_preview(self):
        if not self._selected_file_path:
            return

        selected_path = Path(self._selected_file_path)
        if selected_path in self._preview_cache:
            self._view.set_image_preview(self._preview_cache[selected_path])
            return

        try:
            if selected_path.suffix.lower() in (".dcm", ".dicom"):
                b64 = DicomPreviewService.dicom_to_base64(str(selected_path))
                self._preview_cache[selected_path] = b64
                self._view.set_image_preview(b64)
        except Exception as e:
            self._view.create_alert(f"Preview failed: {e}")

