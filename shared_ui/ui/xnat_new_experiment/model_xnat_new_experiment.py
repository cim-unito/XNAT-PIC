class ModelXnatNewExperiment:

    @staticmethod
    def can_submit(parent_project: str, parent_subject: str,
                   experiment_label: str) -> bool:
        return bool((parent_project or "").strip()) and bool((parent_subject or "").strip()) and bool((experiment_label or "").strip())

    @staticmethod
    def build_payload(
            parent_project: str,
            parent_subject: str,
            experiment_label: str,
    ) -> dict[str, str]:
        return {
            "parent_project": (parent_project or "").strip(),
            "parent_subject": (parent_subject or "").strip(),
            "experiment_label": (experiment_label or "").strip(),
        }