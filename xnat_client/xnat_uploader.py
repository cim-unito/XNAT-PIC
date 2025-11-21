from pathlib import Path


class UploaderService:
    def __init__(self):
        pass

    def iter_subject_experiments(self, base_path: Path):
        subjects = [p for p in base_path.iterdir() if p.is_dir()]
        if not subjects:
            raise ValueError("No subject folders found in selected path.")

        result = []
        for subj in subjects:
            exps = [e for e in subj.iterdir() if e.is_dir()]
            if not exps:
                continue
            for exp_folder in exps:
                subject_id = subj.name.replace(".", "_")
                experiment_id = "_".join(
                    [
                        base_path.name.replace("_dcm", ""),
                        subj.name.replace(".", "_"),
                        exp_folder.name.replace(".", "_"),
                    ]
                ).replace(" ", "_")
                result.append((subject_id, experiment_id, exp_folder))

        if not result:
            raise ValueError("No experiment folders found.")
        return result

    def upload_project_folder(
            self,
            base_path: Path,
            project_id: str,
            upload_experiment_fn,
            progress_callback=None,
    ):
        items = self.iter_subject_experiments(base_path)
        total = len(items)
        done = 0

        for subject_id, experiment_id, exp_folder in items:
            upload_experiment_fn(exp_folder, project_id, subject_id, experiment_id)
            done += 1
            if progress_callback:
                progress_callback(done, total)
