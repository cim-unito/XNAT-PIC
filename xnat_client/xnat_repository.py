import shutil
import tempfile
import time
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

    def list_experiments(self, project_id, subject_id):
        subj = self._session.projects[project_id].subjects[subject_id]

        return [
            {"id": e.id, "label": e.label or e.id}
            for e in subj.experiments.values()
        ]

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

                imported_session = self._session.services.import_(
                    zip_dst,
                    project=project_id,
                    subject=subject_id,
                    experiment=experiment_id,
                    import_handler="DICOM-zip",
                    overwrite="append",
                    quarantine=False,
                )

                self._session.clearcache()
                self._rebuild_and_archive_imported_session(
                    project_id=project_id,
                    subject_id=subject_id,
                    experiment_id=experiment_id,
                    imported_session=imported_session,
                    max_attempts=8,
                    poll_interval_seconds=2.0,
                )
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
                    self._upload_resource_file(resource, local_file, remote_path)
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

    def _rebuild_and_archive_imported_session(
            self,
            project_id: str,
            subject_id: str,
            experiment_id: str,
            imported_session,
            max_attempts: int,
            poll_interval_seconds: float,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if poll_interval_seconds < 0:
            raise ValueError("poll_interval_seconds must be >= 0")

        last_status = None
        rebuild_requested = False
        archive_requested = False
        reusable_session = self._as_prearchive_session(imported_session)
        for attempt in range(1, max_attempts + 1):
            prearchive_session = reusable_session
            if prearchive_session is None:
                prearchive_session = self._find_prearchive_session(
                    project_id=project_id,
                    subject_id=subject_id,
                    experiment_id=experiment_id,
                )

            if prearchive_session is None:
                if self.experiment_exists(project_id, subject_id, experiment_id):
                    return

                if attempt < max_attempts:
                    time.sleep(poll_interval_seconds)
                    continue

                break

            status = str(getattr(prearchive_session, "status", "") or "").strip().lower()
            last_status = status or "unknown"

            if "receiv" in status:
                if not rebuild_requested:
                    prearchive_session.rebuild(asynchronous=False)
                    rebuild_requested = True
                    archive_requested = False
                self._session.clearcache()
                reusable_session = None
                if attempt < max_attempts:
                    time.sleep(poll_interval_seconds)
                continue

            if any(in_progress in status for in_progress in {"rebuild", "archiv", "process", "queue"}):
                self._session.clearcache()
                reusable_session = None
                if attempt < max_attempts:
                    time.sleep(poll_interval_seconds)
                    continue
                return

            if not archive_requested:
                prearchive_session.archive(
                    overwrite="append",
                    quarantine=False,
                    project=project_id,
                    subject=subject_id,
                    experiment=experiment_id,
                )
                archive_requested = True
                self._session.clearcache()
                reusable_session = None

            if self.experiment_exists(project_id, subject_id, experiment_id):
                return

            if attempt < max_attempts:
                time.sleep(poll_interval_seconds)

        if last_status and any(in_progress in last_status for in_progress in {"rebuild", "archiv", "process", "queue"}):
            return

        raise RuntimeError(
            "Unable to archive imported session after "
            f"{max_attempts} attempts. Last prearchive status: {last_status}."
        )

    def _find_prearchive_session(self,
                                 project_id: str,
                                 subject_id: str,
                                 experiment_id: str):
        try:
            sessions = self._session.prearchive.sessions(project=project_id)
        except TypeError:
            sessions = self._session.prearchive.sessions()

        normalized_subject = str(subject_id or "").strip()
        normalized_experiment = str(experiment_id or "").strip()

        for prearchive_session in sessions:
            session_project = str(getattr(prearchive_session, "project", "") or "").strip()
            if session_project and session_project != project_id:
                continue

            session_subject = str(getattr(prearchive_session, "subject", "") or "").strip()
            if session_subject and session_subject != normalized_subject:
                continue

            session_keys = {
                str(getattr(prearchive_session, "name", "") or "").strip(),
                str(getattr(prearchive_session, "label", "") or "").strip(),
                str(getattr(prearchive_session, "folder_name", "") or "").strip(),
                str(getattr(prearchive_session, "id", "") or "").strip(),
            }
            if normalized_experiment in session_keys:
                return prearchive_session

        return None

    @staticmethod
    def _as_prearchive_session(imported_session):
        if imported_session is None:
            return None

        has_archive = callable(getattr(imported_session, "archive", None))
        has_rebuild = callable(getattr(imported_session, "rebuild", None))
        if has_archive and has_rebuild:
            return imported_session

        return None

    @staticmethod
    def _upload_resource_file(resource, local_file: Path, remote_path: str) -> None:
        """Upload ``local_file`` preserving binary content."""
        upload_method = getattr(resource, "upload", None)
        if callable(upload_method):
            upload_method(str(local_file), remotepath=remote_path, overwrite=True)
            return

        with local_file.open("rb") as file_stream:
            resource.upload_data(
                file_stream.read(),
                remotepath=remote_path,
                overwrite=True,
            )

    @staticmethod
    def _sanitize_label(label: str):
        cleaned = "".join(
            ch if (ch.isalnum() or ch in {"_", "-"}) else "_"
            for ch in label.strip()
        )
        return cleaned or None
