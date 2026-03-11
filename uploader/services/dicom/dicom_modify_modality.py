from pathlib import Path
from typing import Iterable

from pydicom import dcmread


class DicomModifyModality:
    @staticmethod
    def modify_modality(
        dicom_files_to_modify: Iterable[Path],
        new_modality: str,
    ) -> None:
        """Update the ``Modality`` tag for each provided DICOM file."""
        for dicom_scan in dicom_files_to_modify:
            ds = dcmread(dicom_scan)
            ds.Modality = new_modality
            dicom_scan.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(dicom_scan, write_like_original=False)