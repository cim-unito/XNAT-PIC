class ModelXnatNewProject:

    @staticmethod
    def generate_project_id(title: str) -> str:
        return title.lower().replace(" ", "_")

    @staticmethod
    def can_submit(title: str, project_id: str) -> bool:
        return bool((title or "").strip()) and bool((project_id or "").strip())

    @staticmethod
    def build_payload(title: str, project_id: str, accessibility: str, description: str):
        return {
            "project_name": (title or "").strip(),
            "project_id": (project_id or "").strip(),
            "accessibility": (accessibility or "private").strip(),
            "description": (description or "").strip(),
        }