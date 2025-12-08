import shutil
import tempfile
from pathlib import Path
from typing import List, Dict

from enums.uploader_level import UploaderLevel


class FilesystemService:

    @staticmethod
    def get_list_directory_treeview(path: Path) -> List[Dict]:
        """
        Returns a list of dict with name, path, is_dir.
        """
        try:
            # Sorting criterion:
            # - All directories before files
            # - Within groups (directories and files), case-insensitive
            # alphabetical sorting
            children = sorted(
                path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            return [{
                "name": "[access denied]",
                "path": path,
                "is_dir": False
            }]
        except FileNotFoundError:
            raise ValueError(f"Path not found: {path}")

        items = []
        for child in children:
            if child.name.startswith("."):
                continue

            items.append({
                "name": child.name,
                "path": child,
                "is_dir": child.is_dir(),
            })

        return items

    @staticmethod
    def _find_experiments(path, level):
        experiment_list = []
        if level == UploaderLevel.PROJECT:
            # project → subject → experiment
            experiment_list = [
                exp
                for sub in path.iterdir() if sub.is_dir()
                for exp in sub.iterdir() if exp.is_dir()
            ]

        elif level == UploaderLevel.SUBJECT:
            # subject → experiment
            experiment_list = [exp for exp in path.iterdir() if exp.is_dir()]

        elif level == UploaderLevel.EXPERIMENT:
            experiment_list = [path]

        return experiment_list

    @staticmethod
    def get_list_dicom_files(path, level):
        if path is None:
            raise ValueError("Input path not set.")

        experiment = FilesystemService._find_experiments(path,
                                                         level)

        if not experiment:
            raise ValueError("There are no experiments to iterate")

        list_dicom_files = [
            file
            for exp in experiment
            for scan in exp.iterdir() if scan.is_dir()
            for file in scan.iterdir()
            if file.is_file() and file.suffix.lower() in [".dcm", ".dicom"]
        ]

        return list_dicom_files

    @staticmethod
    def create_temp_dicom_upload_directory():
        tmpdir = tempfile.mkdtemp()
        return tmpdir

    @staticmethod
    def copy_dicom_file(input_root, dicom_file, tmpdir):
        src = dicom_file
        dst = tmpdir / dicom_file.relative_to(input_root)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)