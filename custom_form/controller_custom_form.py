from pathlib import Path
import threading
import flet as ft

from enums.custom_form_level import CustomFormLevel
from xnat_client.xnat_custom_form import XnatCustomForm
from xnat_client.xnat_repository import XnatRepository


class ControllerCustomForm:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view_xnat_auth = None
        self._controller_xnat_auth = None

        self._xnat_session = None
        self._xnat_repo = None
        self._xnat_custom_form = None

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
        self._xnat_custom_form = XnatCustomForm(xnat_session)
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
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT)
    # ==========================================================
    def custom_forms_project(self, level):
        """Add/edit custom form at project-level."""
        self._set_level(CustomFormLevel.PROJECT)

    def custom_forms_subject(self, e):
        """Add/edit custom form at subject-level."""
        self._set_level(CustomFormLevel.SUBJECT)

    def custom_forms_experiment(self, e):
        """Add/edit custom form at experiment-level."""
        self._set_level(CustomFormLevel.EXPERIMENT)

        self.load_projects()

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
            self._load_custom_fields()
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
            self._load_custom_fields()
        except Exception as e:
            self._view.create_alert(f"Cannot load experiments: {e}")

    def on_experiment_selected(self, e):
        self._load_custom_fields()

    # ==========================================================
    # LOAD CUSTOM FIELD
    # ==========================================================
    def _load_custom_fields(self):
        project_id = self._view.dd_xnat_project.value
        subject_id = self._view.dd_xnat_subject.value
        experiment_id = self._view.dd_xnat_experiment.value

        try:
            if self._model.level == CustomFormLevel.PROJECT:
                if not project_id:
                    return
                fields = self._xnat_custom_form.get_custom_fields(project_id)
            elif self._model.level == CustomFormLevel.SUBJECT:
                if not project_id or not subject_id:
                    return
                fields = self._xnat_custom_form.get_custom_fields(project_id,
                                                                  subject_id)
            elif self._model.level == CustomFormLevel.EXPERIMENT:
                if not project_id or not subject_id or not experiment_id:
                    return
                fields = self._xnat_custom_form.get_custom_fields(project_id,
                                                                  subject_id,
                                                                  experiment_id)
            else:
                return

            self._view.set_custom_fields(**fields)
        except Exception as e:
            self._view.create_alert(f"Cannot load custom fields: {e}")

    # -------------------------------------------------------
    # SAVE CUSTOM FIELDS
    # -------------------------------------------------------
    def on_save_clicked(self, e):
        project_id = self._view.dd_xnat_project.value
        subject_id = self._view.dd_xnat_subject.value
        experiment_id = self._view.dd_xnat_experiment.value

        payload = {
            "group": self._view.txt_group.value,
            "timepoint": self._view.txt_timepoint.value,
            "dose": self._view.txt_dose.value,
        }

        try:
            if self._model.level == CustomFormLevel.PROJECT:
                if not project_id:
                    raise ValueError("Please select a project before saving.")
                self._xnat_custom_form.update_custom_fields(project_id,
                                                            **payload)
            elif self._model.level == CustomFormLevel.SUBJECT:
                if not project_id or not subject_id:
                    raise ValueError(
                        "Please select a project and subject before saving."
                    )
                self._xnat_custom_form.update_custom_fields(
                    project_id, subject_id, **payload
                )
            elif self._model.level == CustomFormLevel.EXPERIMENT:
                if not project_id or not subject_id or not experiment_id:
                    raise ValueError(
                        "Please select project, subject, and experiment before"
                        "saving."
                    )
                self._xnat_custom_form.update_custom_fields(
                    project_id, subject_id, experiment_id, **payload
                )
            else:
                return

            self._view.create_alert("Custom fields saved successfully.")
        except Exception as exc:
            self._view.create_alert(f"Cannot save custom fields: {exc}")

    def _set_level(self, level):
        self._model.level = level
        """Set the custom forms level and update the view mode."""
        if level == CustomFormLevel.PROJECT:
            self._view.set_mode(xnat_subject=False, xnat_experiment=False)
        elif level == CustomFormLevel.SUBJECT:
            self._view.set_mode(xnat_subject=True, xnat_experiment=False)
        elif level == CustomFormLevel.EXPERIMENT:
            self._view.set_mode(xnat_subject=True, xnat_experiment=True)

        self.load_projects()