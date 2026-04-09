from xnat_client.xnat_session import XnatSession


class XnatCustomForm:
    _PROJECT_FORM_ID = "9ba2982a-eabf-458a-adb7-0277a426c308"
    _SUBJECT_FORM_ID = "26d74863-12fe-4b4d-bb83-2bd4ec202c54"
    _EXPERIMENT_FORM_ID = "ca3e738a-ade4-46dc-bd29-83061dcd802d"

    def __init__(self, xnat_session: XnatSession):
        if not xnat_session.session:
            raise ValueError("XNAT session not connected.")
        self._session = xnat_session.session

    def _custom_form_id(self, subject_id=None, experiment_id=None):
        if experiment_id:
            return self._EXPERIMENT_FORM_ID
        if subject_id:
            return self._SUBJECT_FORM_ID
        return self._PROJECT_FORM_ID



    def get_custom_fields(self, project_id, subject_id=None, experiment_id=None):
        """Return custom fields (group, timepoint, dose) for the given level."""

        uri = self._custom_fields_uri(project_id, subject_id, experiment_id)

        response = self._session.get(uri)
        response.raise_for_status()

        payload = response.json() or {}
        form_id = self._custom_form_id(subject_id, experiment_id)

        selected_form = payload.get(form_id, {})

        if not isinstance(selected_form, dict):
            selected_form = {}

        if not selected_form:
            for value in payload.values():
                if isinstance(value, dict):
                    selected_form = value
                    break

        return {
            "group": selected_form.get("group", ""),
            "timepoint": selected_form.get("timepoint", ""),
            "dose": selected_form.get("dose", ""),
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

        If XNAT returns an empty payload, create a new entry keyed by the
        configured form id for the current scope.
        """

        uri = self._custom_fields_uri(project_id, subject_id, experiment_id)

        response = self._session.get(uri)
        response.raise_for_status()

        payload = response.json() or {}
        form_id = self._custom_form_id(subject_id, experiment_id)

        updates = {
            "group": group,
            "timepoint": timepoint,
            "dose": dose,
        }

        existing_entry = payload.get(form_id)
        if not isinstance(existing_entry, dict):
            existing_entry = {}

        existing_entry.update(updates)
        payload[form_id] = existing_entry

        put_response = self._session.put(
            uri, json=payload, headers={"Content-Type": "application/json"}
        )
        put_response.raise_for_status()

        return payload

    @staticmethod
    def _custom_fields_uri(project_id, subject_id=None, experiment_id=None):
        base_uri = f"/xapi/custom-fields/projects/{project_id}"

        if experiment_id:
            return (
                f"{base_uri}/subjects/{subject_id}/experiments/{experiment_id}/fields"
            )

        if subject_id:
            return f"{base_uri}/subjects/{subject_id}/fields"

        return f"{base_uri}/fields"