from bs4 import BeautifulSoup

from xnat_client.xnat_session import XnatSession


class XnatRepository:
    def __init__(self, xnat_session: XnatSession):
        if not xnat_session.session:
            raise ValueError("XNAT session not connected.")
        self._session = xnat_session.session

    def list_projects(self) -> list[dict[str, str]]:
        return [
            {"id": p.id, "name": p.name}
            for p in self._session.projects.values()
        ]

    def project_exists(self, project_id: str) -> bool:
        if not project_id:
            return False
        return project_id in self._session.projects

    def list_subjects(self, project_id: str) -> list[dict[str, str]]:
        prj = self._session.projects[project_id]

        return [
            {"id": s.id, "label": s.label or s.id}
            for s in prj.subjects.values()
        ]

    def subject_exists(self, project_id: str, subject_label: str) -> bool:
        if not project_id or not subject_label:
            return False

        subjects = self.list_subjects(project_id)

        return any(
            s["label"] == subject_label
            for s in subjects
        )

    def list_experiments(self, project_id: str, subject_id: str) -> list[dict[str, str]]:
        subj = self._session.projects[project_id].subjects[subject_id]

        return [
            {"id": e.id, "label": e.label or e.id}
            for e in subj.experiments.values()
        ]

    def experiment_exists(self, project_id: str, subject_id: str, experiment_label: str) -> bool:
        if not project_id or not subject_id or not experiment_label:
            return False

        try:
            experiments = self.list_experiments(project_id, subject_id)
        except Exception:
            return False

        return any(
            e["label"] == experiment_label
            for e in experiments
        )

    def create_project(self, data: dict[str, str]) -> dict[str, str]:
        session = self._session

        project_id = data.get("project_id")

        if not project_id:
            raise ValueError("Project ID is required.")

        project_name = str(data.get("project_name") or project_id).strip()
        project_description = str(data.get("description") or "").strip()
        project_access = str(data.get("accessibility") or "private").strip().lower()

        valid_access = {"private", "protected", "public"}
        if project_access not in valid_access:
            raise ValueError(
                f"Invalid accessibility '{project_access}'. "
                f"Expected one of: {sorted(valid_access)}"
            )

        try:
            project = session.classes.ProjectData(
                parent=session,
                secondary_id=project_id,
                id_=project_id,
                name=project_name,
            )

            project.description = project_description
            session.put(f"/data/projects/{project_id}/accessibility/{project_access}")
            session.clearcache()
        except Exception as err:
            error_message = self._extract_error_message(err)

            raise RuntimeError(
                error_message
            ) from err

        return {
            "project_id": project.id,
            "project_name": project.name,
            "accessibility": project_access,
            "description": project_description or "",
        }

    def create_subject(self, data: dict[str, str]) -> dict[str, str]:
        session = self._session

        project_id = data.get("parent_project")
        subject_label = data.get("subject_label")
        if not project_id:
            raise ValueError("parent_project is required.")
        if not subject_label:
            raise ValueError("subject_label is required.")

        try:
            project = session.projects[project_id]
            subject = session.classes.SubjectData(
                parent = project,
                label = subject_label,
            )
            session.clearcache()
        except Exception as err:
            error_message = self._extract_error_message(err)

            raise RuntimeError(
                error_message
            ) from err

        return {
            "project_id": subject.project,
            "subject_label": subject.label,
            "subject_id": subject.id,
        }

    def create_experiment(self, data: dict[str, str]) -> dict[str, str]:
        session = self._session

        project_id = data.get("parent_project")
        subject_id = data.get("parent_subject")
        experiment_label = data.get("experiment_label")

        if not project_id:
            raise ValueError("parent_project is required.")
        if not subject_id:
            raise ValueError("parent_subject is required.")
        if not experiment_label:
            raise ValueError("experiment_id is required.")

        try:
            subject = session.projects[project_id].subjects[subject_id]
            experiment = session.classes.MrSessionData(
                parent = subject,
                label = experiment_label,
            )
            session.clearcache()
        except Exception as err:
            error_message = self._extract_error_message(err)

            raise RuntimeError(
                error_message
            ) from err

        return {
            "project_id": experiment.project,
            "subject_id": experiment.subject_id,
            "experiment_label": experiment.label,
            "experiment_id": experiment.id,
        }

    @staticmethod
    def _extract_error_message(err: Exception) -> str:
        error_text = getattr(err, "text", None) or str(err)

        soup = BeautifulSoup(error_text, "html.parser")
        body = soup.body

        error_message = (
            body.get_text(" ", strip=True)
            if body
            else soup.get_text(" ", strip=True)
        )

        error_message = error_message.replace(
            "You can get technical details here . Please continue your visit at our home page .",
            ""
        ).strip()

        return error_message