import shutil
import tempfile
from pathlib import Path

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

    def list_subjects(self, project_id):
        prj = self._session.projects[project_id]

        return [
            {"id": s.id, "label": s.label or s.id}
            for s in prj.subjects.values()
        ]

    def list_experiments(self, project_id, subject_id):
        subj = self._session.projects[project_id].subjects[subject_id]

        return [
            {"id": e.id, "label": e.label or e.id}
            for e in subj.experiments.values()
        ]

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

        project = session.projects[project_id]
        subject = session.classes.SubjectData(
            parent = project,
            id_ = subject_id,
            label = subject_id,
            name = subject_label,
        )

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

        subject = session.projects[project_id].subjects[subject_id]
        session.classes.MrSessionData(
            parent = subject,
            id_ = experiment_id,
            label = experiment_id,
            name = experiment_label,
        )

        return {
            "project_id": project_id,
            "subject_id": subject_id,
            "experiment_id": experiment_id,
            "experiment_name": experiment_label,
        }

    def upload_dicom(self, exp_folder, project_id, subject_id,
                     experiment_id):

        exp_folder = Path(exp_folder)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                zip_dst = shutil.make_archive(
                    base_name=str(tmpdir / experiment_id),
                    format="zip",
                    root_dir=str(exp_folder)
                )

                self._session.services.import_(
                    zip_dst,
                    project=project_id,
                    subject=subject_id,
                    experiment=experiment_id,
                    import_handler="DICOM-zip",
                    overwrite="append",
                    quarantine="false"
                )

                self._session.clearcache()

        except Exception as e:
            raise RuntimeError(f"Upload failed: {e}")

    def upload_files_resources(
            self,
            source_folder,
            project_id,
            subject_id,
            experiment_id,
            default_resource_label="NON_DICOM",
    ):
        source_folder = Path(source_folder)

        resource_label = source_folder.name if source_folder.name else default_resource_label

        if not source_folder.exists() or not source_folder.is_dir():
            raise ValueError("Resource source folder is not valid.")

        if not project_id or not subject_id or not experiment_id:
            raise ValueError(
                "Project, subject, and experiment are required "
                "to upload resources."
            )

        files_by_resource = self._group_resource_files(
            source_folder,
            resource_label,
        )

        if not files_by_resource:
            raise ValueError("No non-DICOM files found to upload.")

        uploaded_files = 0
        failed_uploads = []
        for resource_label, resources in files_by_resource.items():
            try:
                resource = self._get_or_create_experiment_resource(
                    project_id,
                    subject_id,
                    experiment_id,
                    resource_label,
                )
            except KeyError as err:
                raise ValueError(
                    "Invalid XNAT target. Verify project, subject and experiment "
                    "exist and are accessible."
                ) from err

            for local_file, remote_path in resources:
                try:
                    resource.upload_data(
                        str(local_file),
                        remotepath=remote_path,
                        overwrite=True,
                    )
                    uploaded_files += 1
                except Exception as err:
                    failed_uploads.append(
                        f"{local_file.name}: {err}"
                    )

        self._session.clearcache()

        if failed_uploads:
            failures_preview = "; ".join(failed_uploads[:5])
            if len(failed_uploads) > 5:
                failures_preview += "; ..."
            raise RuntimeError(
                "Resources upload completed with errors "
                f"({uploaded_files} uploaded, {len(failed_uploads)} failed). "
                f"Failures: {failures_preview}"
            )
        return uploaded_files

    def _group_resource_files(self, source_folder: Path,
                              resource_label: str):
        sanitized_label = self._sanitize_label(resource_label)
        grouped = {sanitized_label: []}
        for local_file in source_folder.rglob("*"):
            if not local_file.is_file():
                continue

            if local_file.suffix.lower() in {".dcm", ".dicom"}:
                continue

            relative_path = local_file.relative_to(source_folder)
            remote_path = relative_path.as_posix()

            grouped[sanitized_label].append(
                (local_file, remote_path)
            )

        if not grouped[sanitized_label]:
            return {}

        return grouped

    def _get_or_create_experiment_resource(self,
                                           project_id: str,
                                           subject_id: str,
                                           experiment_id: str,
                                           resource_label: str):

        session = self._session
        xnat_experiment = session.projects[project_id].subjects[subject_id].experiments[experiment_id]
        resource_label = self._sanitize_label(resource_label)

        if not resource_label in xnat_experiment.resources:
            self._session.classes.ResourceCatalog(
                parent=xnat_experiment,
                label=resource_label,
            )
            self._session.clearcache()

        resource = xnat_experiment.resources[resource_label]
        return resource

    @staticmethod
    def _sanitize_label(label: str):
        cleaned = "".join(
            ch if (ch.isalnum() or ch in {"_", "-"}) else "_"
            for ch in label.strip()
        )
        return cleaned or None
