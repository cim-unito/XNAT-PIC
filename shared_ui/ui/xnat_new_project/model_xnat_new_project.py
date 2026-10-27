class ModelXnatNewProject:

    @staticmethod
    def can_submit(project_name: str, project_id: str) -> bool:
        return bool((project_name or "").strip()) and bool((project_id or "").strip())

    @staticmethod
    def build_payload(project_name: str, project_id: str, accessibility: str, description: str) -> dict[str, str]:
        return {
            "project_name": (project_name or "").strip(),
            "project_id": (project_id or "").strip(),
            "accessibility": (accessibility or "private").strip().lower(),
            "description": (description or "").strip(),
        }