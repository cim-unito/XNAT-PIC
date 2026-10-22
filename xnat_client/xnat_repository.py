from xnat_client.xnat_session import XnatSession


class XnatRepository:
    def __init__(self, xnat_session: XnatSession):
        if not xnat_session.session:
            raise ValueError("XNAT session not connected.")
        self._session = xnat_session.session

    def list_projects(self):
        return [
            {"id": p.id, "label": p.name}
            for p in self._session.projects.values()
        ]

    def project_exists(self, project_id: str):
        normalized_project_id = self._sanitize_label(str(project_id or "").strip())
        if not normalized_project_id:
            return False
        return normalized_project_id in self._session.projects

    def list_subjects(self, project_id):
        prj = self._session.projects[project_id]

        return [
            {"id": s.id, "label": s.label or s.id}
            for s in prj.subjects.values()
        ]

    def subject_exists(self, project_id: str, subject_id: str):
        normalized_project_id = self._sanitize_label(str(project_id or "").strip())
        normalized_subject_id = self._sanitize_label(str(subject_id or "").strip())
        if not normalized_project_id or not normalized_subject_id:
            return False
        try:
            subjects = self.list_subjects(normalized_project_id)
        except Exception:
            return False
        return any(
            s["id"] == normalized_subject_id or s["label"] == normalized_subject_id
            for s in subjects
        )

    def create_project(self, data):
        session = self._session

        project_id = str(data.get("project_id") or "").strip()
        project_id = self._sanitize_label(project_id)

        if not project_id:
            raise ValueError("Project ID is required.")

        if project_id in session.projects:
            raise ValueError(f"Project '{project_id}' already exists.")

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
                label=project_id,
                name=project_name,
            )

            project.description = project_description
            session.put(f"/data/projects/{project_id}/accessibility/{project_access}")
            session.clearcache()
        except Exception as err:
            raise RuntimeError(
                f"Project creation failed for '{project_id}': {err}"
            ) from err

        return {
            "project_id": project_id,
            "project_name": project_name,
            "accessibility": project_access,
            "description": project_description,
        }

    def create_subject(self, data):
        session = self._session

        project_id = str(data["parent_project"]).strip()
        subject_id = str(data["subject_id"]).strip()
        subject_id = self._sanitize_label(subject_id)
        if not project_id:
            raise ValueError("parent_project is required.")
        if not subject_id:
            raise ValueError("subject_id is required.")

        subject_name = str(data.get("subject_name", "")).strip()
        subject_label = subject_name or subject_id

        try:
            project = session.projects[project_id]
            subject = session.classes.SubjectData(
                parent = project,
                id_ = subject_id,
                label = subject_id,
                name = subject_label,
            )
            session.clearcache()
        except Exception as err:
            raise RuntimeError(
                f"Subject creation failed for '{project_id}': {err}"
            ) from err

        return {
            "project_id": project_id,
            "subject_name": subject_label,
            "subject_id": subject_id,
        }

    def create_experiment(self, data):
        session = self._session

        project_id = str(data["parent_project"]).strip()
        subject_id = str(data["subject_project"]).strip()
        experiment_id = str(data["experiment_id"]).strip()
        experiment_id = self._sanitize_label(experiment_id)
        if not project_id:
            raise ValueError("parent_project is required.")
        if not subject_id:
            raise ValueError("subject_project is required.")
        if not experiment_id:
            raise ValueError("experiment_id is required.")

        experiment_name = str(data.get("experiment_name", "")).strip()
        experiment_label = experiment_name or experiment_id

        try:
            subject = session.projects[project_id].subjects[subject_id]
            session.classes.MrSessionData(
                parent = subject,
                id_ = experiment_id,
                label = experiment_id,
                name = experiment_label,
            )
            session.clearcache()
        except Exception as err:
            raise RuntimeError(
                f"Project creation failed for '{project_id}': {err}"
            ) from err

        return {
            "project_id": project_id,
            "subject_id": subject_id,
            "experiment_id": experiment_id,
            "experiment_name": experiment_label,
        }

    def experiment_exists(self, project_id: str, subject_id: str, experiment_id: str):
        normalized_project_id = self._sanitize_label(str(project_id or "").strip())
        normalized_subject_id = self._sanitize_label(str(subject_id or "").strip())
        normalized_experiment_id = self._sanitize_label(str(experiment_id or "").strip())

        if not normalized_project_id or not normalized_subject_id or not normalized_experiment_id:
            return False

        try:
            experiments = self.list_experiments(normalized_project_id, normalized_subject_id)
        except Exception:
            return False

        return any(
            e["id"] == normalized_experiment_id or e["label"] == normalized_experiment_id
            for e in experiments
        )

    def list_experiments(self, project_id, subject_id):
        subj = self._session.projects[project_id].subjects[subject_id]

        return [
            {"id": e.id, "label": e.label or e.id}
            for e in subj.experiments.values()
        ]

    @staticmethod
    def _sanitize_label(label: str):
        cleaned = "".join(
            ch if (ch.isalnum() or ch in {"_", "-"}) else "_"
            for ch in label.strip()
        )
        return cleaned or None
