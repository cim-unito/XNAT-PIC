import shutil
from pathlib import Path
from typing import List, Dict

from enums.converter_level import ConverterLevel
from enums.converter_type import ConverterType


class FilesystemService:
    @staticmethod
    def get_input_scans(input_root: Path, level: ConverterLevel,
                        conversion_type: ConverterType) -> list[Path]:

        if input_root is None:
            raise ValueError("Input path not set.")
        if not input_root.exists():
            raise FileNotFoundError(f"Input folder '{input_root}' does not exist.")
        if not input_root.is_dir():
            raise NotADirectoryError(f"'{input_root}' is not a valid folder.")
        if not any(input_root.iterdir()):
            raise ValueError(
                f"The selected folder '{input_root}' is empty."
            )

        experiment_list = FilesystemService._find_experiments(input_root,
                                                              level)

        if not experiment_list:
            raise ValueError(
                f"No experiments found in '{input_root}' for level '{level.value}'."
            )

        return FilesystemService._filter_scans(experiment_list,
                                               conversion_type,
                                               level)

    @staticmethod
    def get_output_scans(input_scans: list, input_root: Path, output_root: Path):
        if output_root is None or input_root is None:
            raise ValueError("Paths not set.")
        scan_converted = [
            output_root / p.relative_to(input_root)
            for p in input_scans
        ]
        return scan_converted

    @staticmethod
    def create_dicom_output_folder(output_root: Path, overwrite: bool):
        if output_root is None:
            raise ValueError("Output path not set.")

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
                    raise FileExistsError(
                        f"The folder '{output_root}' already exists and "
                        f"'overwrite' is False."
                    )
            else:
                raise NotADirectoryError(
                    f"'{output_root}' exists but is not a directory."
                )
        else:
            print(f"Create the folder '{output_root}'.")
            output_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def delete_folder(dst: Path):
        if dst.is_dir():
            shutil.rmtree(dst)

    @staticmethod
    def _find_experiments(path: Path, level: ConverterLevel) -> list[Path]:
        experiment_list = []
        if level == ConverterLevel.PROJECT:
            # project → subject → experiment
            experiment_list = [
                exp
                for sub in path.iterdir() if sub.is_dir()
                for exp in sub.iterdir() if exp.is_dir()
            ]

        elif level == ConverterLevel.SUBJECT:
            # subject → experiment
            experiment_list = [exp for exp in path.iterdir() if exp.is_dir()]

        elif level == ConverterLevel.EXPERIMENT:
            experiment_list = [path]

        return experiment_list

    @staticmethod
    def _is_bruker_scan(scan: Path) -> bool:
        """A Bruker scan is valid if a '2dseq' file appears in ("*/*/2dseq")."""
        has_2dseq = any(
            (level2 / "2dseq").is_file()
            for level1 in scan.iterdir()
            if level1.is_dir()
            for level2 in level1.iterdir()
            if level2.is_dir()
        )
        return has_2dseq

    @staticmethod
    def _is_ivis_scan(scan: Path) -> bool:
        """An IVIS scan is valid if it contains a TIFF file
        and a file with 'clickinfo' in its name.
        """
        has_tiff = False
        has_clickinfo = False

        for f in scan.iterdir():
            if not f.is_file():
                continue

            if f.suffix.lower() in {".tif", ".tiff"}:
                has_tiff = True

            if "clickinfo" in f.name.lower():
                has_clickinfo = True

            if has_tiff and has_clickinfo:
                return True

        return False

    @staticmethod
    def _filter_scans(
            experiment_list: list[Path],
            conversion_type: ConverterType,
            level: ConverterLevel,
    ) -> list[Path]:

        if conversion_type == ConverterType.IVIS2DICOM:
            if level == ConverterLevel.EXPERIMENT:
                if not experiment_list:
                    return []

                scan = experiment_list[0]
                return [scan] if FilesystemService._is_ivis_scan(scan) else []

            is_valid_scan = FilesystemService._is_ivis_scan

        elif conversion_type == ConverterType.BRUKER2DICOM:
            is_valid_scan = FilesystemService._is_bruker_scan

        else:
            return []

        return [
            scan
            for exp in experiment_list
            for scan in exp.iterdir()
            if scan.is_dir() and is_valid_scan(scan)
        ]