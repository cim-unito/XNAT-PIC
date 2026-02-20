class ModelXnatNewProject:

    @staticmethod
    def generate_project_id(project_id: str) -> str:
        return project_id.lower().replace(" ", "_")

    @staticmethod
    def can_submit(project_name: str, project_id: str) -> bool:
        return bool((project_name or "").strip()) and bool((project_id or "").strip())

    @staticmethod
    def build_payload(project_name: str, project_id: str, accessibility: str, description: str):
        return {
            "project_name": (project_name or "").strip(),
            "project_id": (project_id or "").strip(),
            "accessibility": (accessibility or "private").strip(),
            "description": (description or "").strip(),
        }