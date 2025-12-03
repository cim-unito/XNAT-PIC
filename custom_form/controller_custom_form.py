from pathlib import Path
import threading
import flet as ft

from enums.custom_form_level import CustomFormLevel
from xnat_client.xnat_repository import XnatRepository


class ControllerCustomForm:
    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view_xnat_auth = None
        self.__controller_xnat_auth = None

        self._xnat_session = None
        self._xnat_repo = None

    # ==========================================================
    # LOGIN / ROUTE
    # ==========================================================
    def set_xnat_auth(self, view_auth, controller_auth):
        self._view_xnat_auth = view_auth
        self.__controller_xnat_auth = controller_auth

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
    # SET MODE
    # ==========================================================
    def _set_mode_for_level(self, mode):
        if mode == CustomFormLevel.PROJECT:
            self._view.set_mode(
                level_buttons_enabled=False,
                save_enabled=True,
                dd_project=True,
                dd_subject=False,
                dd_experiment=False,
                custom_field_text=True,
            )
        elif mode == CustomFormLevel.SUBJECT:
            self._view.set_mode(
                level_buttons_enabled=False,
                save_enabled=True,
                dd_project=True,
                dd_subject=True,
                dd_experiment=False,
                custom_field_text=True,
            )
        elif mode == CustomFormLevel.EXPERIMENT:
            self._view.set_mode(
                level_buttons_enabled=False,
                save_enabled=True,
                dd_project=True,
                dd_subject=True,
                dd_experiment=True,
                custom_field_text=True,
            )

        self.load_projects()

    # -------------------------------------------------------
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT)
    # -------------------------------------------------------
    def set_level(self, level):
        self._model.level = level
        self._set_mode_for_level(level)

    def custom_forms_project(self, e):
        self.set_level(CustomFormLevel.PROJECT)

    def custom_forms_subject(self, e):
        self.set_level(CustomFormLevel.SUBJECT)

    def custom_forms_experiment(self, e):
        self.set_level(CustomFormLevel.EXPERIMENT)

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
        print(self._view.dd_xnat_project.value)
        print(self._view.dd_xnat_project.key)
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
            self._view.create_alert(f"Cannot load experiments:z {e}")






