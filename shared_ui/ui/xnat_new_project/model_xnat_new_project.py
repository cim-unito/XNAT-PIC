import re


class ModelXnatNewProject:
    _PROJECT_ID_ALLOWED_CHARS = re.compile(r"[^a-z0-9_]")
    _VALID_ACCESSIBILITY = {"private", "protected", "public"}

    @staticmethod
    def generate_project_id(project_id: str) -> str:
        normalized = (project_id or "").strip().lower().replace(" ", "_")
        normalized = normalized.replace("-", "_").replace(".", "_")
        normalized = ModelXnatNewProject._PROJECT_ID_ALLOWED_CHARS.sub("", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized

    @staticmethod
    def can_submit(project_name: str, project_id: str) -> bool:
        return not ModelXnatNewProject.validate_payload(
            project_name,
            project_id,
            "private",
        )

    @staticmethod
    def validate_payload(project_name: str, project_id: str, accessibility: str) -> list[str]:
        errors = []

        if not (project_name or "").strip():
            errors.append("Project name is required.")

        normalized_project_id = (project_id or "").strip()
        if not normalized_project_id:
            errors.append("Project ID is required.")
        elif "/" in normalized_project_id:
            errors.append("Project ID cannot contain '/'.")

        normalized_accessibility = (accessibility or "private").strip().lower()
        if normalized_accessibility not in ModelXnatNewProject._VALID_ACCESSIBILITY:
            errors.append(
                "Accessibility must be one of: private, protected, public."
            )

        return errors

    @staticmethod
    def build_payload(project_name: str, project_id: str, accessibility: str, description: str):
        return {
            "project_name": (project_name or "").strip(),
            "project_id": (project_id or "").strip(),
            "accessibility": (accessibility or "private").strip().lower(),
            "description": (description or "").strip(),
        }