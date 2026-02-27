class ModelXnatNewSubject:

    @staticmethod
    def generate_subject_id(subject_id: str) -> str:
        return subject_id.lower().replace(" ", "_")

    @staticmethod
    def can_submit(parent_project: str, subject_name: str, subject_id: str) -> bool:
        return bool((parent_project or "").strip()) and bool((subject_name or "").strip()) and bool((subject_id or "").strip())

    @staticmethod
    def build_payload(
            parent_project: str,
            subject_name: str,
            subject_id: str,
            gender: str,
            height_inches: str,
            weight_lbs: str,
            recruitment_source: str,
    ):
        return {
            "parent_project": (parent_project or "").strip(),
            "subject_name": (subject_name or "").strip(),
            "subject_id": (subject_id or "").strip(),
            "gender": (gender or "").strip(),
            "height_inches": (height_inches or "").strip(),
            "weight_lbs": (weight_lbs or "").strip(),
            "recruitment_source": (recruitment_source or "").strip(),
        }