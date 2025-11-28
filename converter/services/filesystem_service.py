import shutil
from pathlib import Path
from typing import List, Dict, Iterable

from xnat.cli.download import experiments

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
            # - Within groups (directories and files), case-insensitive alphabetical sorting
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
        if level == ConverterLevel.project:
            # project → subject → experiment
            experiment_list = [
                exp
                for subject in path.iterdir() if subject.is_dir()
                for exp in subject.iterdir() if exp.is_dir()
            ]

        elif level == ConverterLevel.subject:
            # subject → experiment
            experiment_list = [exp for exp in path.iterdir() if exp.is_dir()]

        elif level == ConverterLevel.experiment:
            experiment_list = [path]

        return experiment_list

    @staticmethod
    def _is_bruker_scan(scan: Path) -> bool:
        """Un Bruker scan è valido se in qualche sotto-cartella compare un file '2dseq'."""
        return any(
            item.is_file() and item.name == "2dseq"
            for item in scan.rglob("*")
        )

    @staticmethod
    def _is_ivis_scan(scan: Path) -> bool:
        """Uno scan IVIS è valido se contiene PNG con '_SEQ' nel nome."""
        return any(
            f.is_file() and f.suffix.lower() == ".png" and "_SEQ" in f.name
            for f in scan.iterdir()
        )

    @staticmethod
    def _filter_scans(experiments: Iterable[Path],
                      conversion_type: ConverterType) -> list[Path]:
        scans = []
        for exp in experiments:
            for scan in exp.iterdir():
                if not scan.is_dir():
                    continue

                if conversion_type == ConverterType.Bruker2Dicom:
                    if FilesystemService._is_bruker_scan(scan):
                        scans.append(scan)

                elif conversion_type == ConverterType.Ivis2Dicom:
                    if FilesystemService._is_ivis_scan(scan):
                        scans.append(scan)

                else:
                    raise ValueError(
                        f"Unknown conversion type: {conversion_type}")

        return scans

    @staticmethod
    def get_valid_scans(path_to_convert: Path, level: ConverterLevel,
                        conversion_type: ConverterType) -> list[Path]:

        if path_to_convert is None:
            raise ValueError("Input path not set.")

        experiments = FilesystemService._find_experiments(path_to_convert,
                                                          level)

        if not experiments:
            raise ValueError("There are no experiments to iterate")

        return FilesystemService._filter_scans(experiments, conversion_type)

    @staticmethod
    def create_dicom_folder(path_converted: Path, overwrite: bool):
        """
        Create (or recreate) the destination folder containing
        the converted dicom files
        """
        if path_converted.exists():
            if path_converted.is_dir():
                if overwrite:
                    print(
                        f"The folder '{path_converted}' already exists."
                        f" Overwrite..."
                    )
                    shutil.rmtree(path_converted)
                    path_converted.mkdir(parents=True, exist_ok=True)
                else:
                    print(
                        f"The folder '{path_converted}' "
                        f"already exists and 'overwrite' is False."
                    )
            else:
                raise NotADirectoryError(
                    f"'{path_converted}' exists but is not a directory."
                )
        else:
            print(f"Create the folder '{path_converted}'.")
            path_converted.mkdir(parents=True, exist_ok=True)

