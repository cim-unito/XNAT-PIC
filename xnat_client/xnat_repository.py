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

        project_id = data["project_id"]
        project_name = data["project_name"]
        description = data["description"]
        access = data["accessibility"]

        session.put(f"/data/projects/{project_id}")

        session.put(f"/data/projects/{project_id}?label={project_name}")
        session.put(f"/data/projects/{project_id}?description={description}")

        session.put(f"/data/projects/{project_id}/accessibility/{access}")

    def create_subject(self, data):
        session = self._session

        project_id = data["parent_project"]
        subject_id = data["subject_id"]
        subject_label = data.get("subject_name", "")

        session.put(f"/data/projects/{project_id}/subjects/{subject_id}")

        if subject_label:
            session.put(
                f"/data/projects/{project_id}/subjects/{subject_id}?label={subject_label}"
            )

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