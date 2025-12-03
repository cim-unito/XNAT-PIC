import shutil
import tempfile
from pathlib import Path

from xnat_client.xnat_session import XnatSession


class XnatCustomForm:
    def __init__(self, xnat_session: XnatSession):
        if not xnat_session.session:
            raise ValueError("XNAT session not connected.")
        self._session = xnat_session.session

    def get_custom_fields(self, project_id, subject_id=None,
                          experiment_id=None):
        """Return custom fields (group, timepoint, dose) for the given level."""

        if experiment_id:
            uri = (
                f"/xapi/custom-fields/projects/{project_id}/subjects/{subject_id}"
                f"/experiments/{experiment_id}/fields"
            )
        elif subject_id:
            uri = (
                f"/xapi/custom-fields/projects/{project_id}/subjects/{subject_id}"
                "/fields"
            )
        else:
            uri = f"/xapi/custom-fields/projects/{project_id}/fields"

        response = self._session.get(uri)
        response.raise_for_status()

        payload = response.json()

        group = ""
        timepoint = ""
        dose = ""

        if payload:
            # API returns a dictionary keyed by xnat id; take the last entry
            # to mirror previous behavior that overwrote the values.
            for value in payload.values():
                group = value.get("group", "")
                timepoint = value.get("timepoint", "")
                dose = value.get("dose", "")

        return {
            "group": group,
            "timepoint": timepoint,
            "dose": dose,
        }