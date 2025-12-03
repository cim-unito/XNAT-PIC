import shutil
import tempfile
from pathlib import Path

from xnat_client.xnat_session import XnatSession


class XnatCustomForm:
    def __init__(self, xnat_session: XnatSession):
        if not xnat_session.session:
            raise ValueError("XNAT session not connected.")
        self._session = xnat_session.session

    def _custom_fields_uri(self, project_id, subject_id=None, experiment_id=None):
        base_uri = f"/xapi/custom-fields/projects/{project_id}"

        if experiment_id:
            return (
                f"{base_uri}/subjects/{subject_id}/experiments/{experiment_id}/fields"
            )

        if subject_id:
            return f"{base_uri}/subjects/{subject_id}/fields"

        return f"{base_uri}/fields"

    def get_custom_fields(self, project_id, subject_id=None, experiment_id=None):
        """Return custom fields (group, timepoint, dose) for the given level."""

        uri = self._custom_fields_uri(project_id, subject_id, experiment_id)

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

    def update_custom_fields(
            self,
            project_id,
            subject_id=None,
            experiment_id=None,
            *,
            group="",
            timepoint="",
            dose="",
    ):
        """Update custom fields for the chosen level.

        Raises a ValueError if XNAT does not already expose the requested
        fields (so the user can add them first).
        """

        uri = self._custom_fields_uri(project_id, subject_id, experiment_id)

        response = self._session.get(uri)
        response.raise_for_status()

        payload = response.json()

        if not payload:
            raise ValueError("No custom fields found on XNAT to update.")

        updates = {
            "group": group,
            "timepoint": timepoint,
            "dose": dose,
        }
        missing_fields = set()

        for entry in payload.values():
            for key, value in updates.items():
                if key in entry:
                    entry[key] = value
                elif value:
                    missing_fields.add(key)

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                "It is not possible to update the following fields because "
                f"they are not valued on XNAT: {missing}. Please add them on "
                "XNAT and try again."
            )

        put_response = self._session.put(
            uri, json=payload, headers={"Content-Type": "application/json"}
        )
        put_response.raise_for_status()

        return payload