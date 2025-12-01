import shutil
from pathlib import Path
from typing import List, Dict

from enums.converter_level import ConverterLevel
from enums.converter_type import ConverterType


class FilesystemService:

    @staticmethod
    def get_list_directory(path: Path) -> List[Dict]:
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
    def _find_experiments(path: Path, level: ConverterLevel) -> list[Path]:
        experiment_list = []
        if level == ConverterLevel.PROJECT:
            # project → subject → experiment
            experiment_list = [
                exp
                for subject in path.iterdir() if subject.is_dir()
                for exp in subject.iterdir() if exp.is_dir()
            ]

        elif level == ConverterLevel.SUBJECT:
            # subject → experiment
            experiment_list = [exp for exp in path.iterdir() if exp.is_dir()]

        elif level == ConverterLevel.EXPERIMENT:
            experiment_list = [path]

        return experiment_list

    @staticmethod
    def _is_bruker_scan(scan: Path) -> bool:
        """A Bruker scan is valid if a '2dseq' file appears in some subfolder."""
        return any(
            item.is_file() and item.name == "2dseq"
            for item in scan.rglob("*")
        )

    @staticmethod
    def _is_ivis_scan(scan: Path) -> bool:
        """An IVIS scan is valid if it contains PNGs with '_SEQ' in the name."""
        return any(
            f.is_file() and f.suffix.lower() == ".png" and "_SEQ" in f.name
            for f in scan.iterdir()
        )

    @staticmethod
    def _filter_scans(experiment_list: List[Path],
                      conversion_type: ConverterType) -> list[Path]:
        scans = []
        for exp in experiment_list:
            for scan in exp.iterdir():
                if not scan.is_dir():
                    continue

                if conversion_type == ConverterType.BRUKER2DICOM:
                    if FilesystemService._is_bruker_scan(scan):
                        scans.append(scan)

                elif conversion_type == ConverterType.IVIS2DICOM:
                    if FilesystemService._is_ivis_scan(scan):
                        scans.append(scan)

        return scans

    @staticmethod
    def get_input_scans(input_root: Path, level: ConverterLevel,
                        conversion_type: ConverterType) -> list[Path]:

        if input_root is None:
            raise ValueError("Input path not set.")

        experiment_list = FilesystemService._find_experiments(input_root,
                                                              level)

        if not experiment_list:
            raise ValueError("There are no experiments to iterate")

        return FilesystemService._filter_scans(experiment_list,
                                               conversion_type)

    @staticmethod
    def get_output_scans(input_scans, input_root, output_root):
        if output_root is None or input_root is None:
            raise ValueError("Paths not set.")
        scan_converted = [
            output_root / p.relative_to(input_root)
            for p in input_scans
        ]
        return scan_converted

    @staticmethod
    def create_dicom_output_folder(output_root: Path, overwrite: bool):
        """
        Create (or recreate) the destination folder containing
        the converted dicom files
        """
        if output_root.exists():
            if output_root.is_dir():
                if overwrite:
                    print(
                        f"The folder '{output_root}' already exists."
                        f" Overwrite..."
                    )
                    shutil.rmtree(output_root)
                    output_root.mkdir(parents=True, exist_ok=True)
                else:
                    print(
                        f"The folder '{output_root}' "
                        f"already exists and 'overwrite' is False."
                    )
            else:
                raise NotADirectoryError(
                    f"'{output_root}' exists but is not a directory."
                )
        else:
            print(f"Create the folder '{output_root}'.")
            output_root.mkdir(parents=True, exist_ok=True)

