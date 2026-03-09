class ModelXnatNewExperiment:

    @staticmethod
    def generate_experiment_id(experiment_id: str) -> str:
        return experiment_id.lower().replace(" ", "_")

    @staticmethod
    def can_submit(parent_project: str, experiment_name: str, experiment_id: str) -> bool:
        return bool((parent_project or "").strip()) and bool((experiment_name or "").strip()) and bool((experiment_id or "").strip())

    @staticmethod
    def build_payload(
            parent_project: str,
            subject_project: str,
            experiment_name: str,
            experiment_id: str,
    ):
        return {
            "parent_project": (parent_project or "").strip(),
            "subject_project": (subject_project or "").strip(),
            "experiment_name": (experiment_name or "").strip(),
            "experiment_id": (experiment_id or "").strip(),
        }