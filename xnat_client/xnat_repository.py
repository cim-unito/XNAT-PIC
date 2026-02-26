import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

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
        if not project_id:
            raise ValueError("Project ID is required.")
        if "/" in project_id:
            raise ValueError("Project ID cannot contain '/'.")

        project_name = str(data.get("project_name") or project_id).strip()
        project_description = str(data.get("description") or "").strip()
        project_access = str(data.get("accessibility") or "private").strip().lower()

        valid_access = {"private", "protected", "public"}
        if project_access not in valid_access:
            raise ValueError(
                f"Invalid accessibility '{project_access}'. "
                f"Expected one of: {sorted(valid_access)}"
            )

        project = session.classes.ProjectData( parent=session,
                                               secondary_id=project_id,
                                               id_=project_id, label=project_id,
                                               name=project_name )

        project.description = project_description

    def create_subject(self, data):
        session = self._session

        project_id = str(data["parent_project"]).strip()
        subject_id = str(data["subject_id"]).strip()
        if not project_id:
            raise ValueError("parent_project is required.")
        if not subject_id:
            raise ValueError("subject_id is required.")

        subject_name = str(data.get("subject_name", "")).strip()
        subject_label = subject_name or subject_id
        subject_fields = {
            "demographics/gender": data.get("gender", ""),
            "demographics/handedness": data.get("handedness", ""),
            "demographics/education": data.get("education", ""),
            "demographics/race": data.get("race", ""),
            "demographics/ethnicity": data.get("ethnicity", ""),
            "demographics/height": data.get("height_inches", ""),
            "demographics/weight": data.get("weight_lbs", ""),
            "demographics/recruitment_src": data.get("recruitment_source", ""),
            "demographics/dob": data.get("date_of_birth", ""),
            "demographics/yob": data.get("year_of_birth", ""),
            "demographics/age": data.get("age", ""),
        }

        project = session.projects[project_id]
        subject = session.classes.SubjectData(
            name=subject_id,
            label=subject_label,
            parent=project
        )

        subject.demographics.gender = data.get("gender", "").lower()
        subject.demographics.handedness = data.get("handedness", "").lower()
        subject.demographics.education = int(data.get("education", ""))
        subject.demographics.race = data.get("race", "")
        subject.demographics.height = data.get("height_inches", "")


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