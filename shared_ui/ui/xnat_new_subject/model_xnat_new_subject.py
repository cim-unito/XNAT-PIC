class ModelXnatNewSubject:

    @staticmethod
    def can_submit(parent_project: str, subject_label: str) -> bool:
        return bool((parent_project or "").strip()) and bool((subject_label or "").strip())

    @staticmethod
    def build_payload(
            parent_project: str,
            subject_label: str,
    ) -> dict[str, str]:
        return {
            "parent_project": (parent_project or "").strip(),
            "subject_label": (subject_label or "").strip(),
        }