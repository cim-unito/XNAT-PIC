import base64
import io
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image
from pydicom import dcmread
from pydicom.uid import UID
from pydicom.datadict import dictionary_VR


class ModelUploader:
    def __init__(self):
        self._path_to_upload = None
        self._level = None
        self._scan_to_upload = None

    def list_directory(self, path: Path) -> list[dict]:
        path = Path(path)
        items = []
        try:
            for child in sorted(path.iterdir()):
                if child.name.startswith("."):
                    continue
                items.append({
                    "name": child.name,
                    "path": str(child),
                    "is_dir": child.is_dir()
                })
        except PermissionError:
            items.append({
                "name": "[access denied]",
                "path": "",
                "is_dir": False
            })
        return items

    def get_valid_scans(self):
        if self._path_to_upload is None:
            raise ValueError("Upload path not set.")

        experiment = []

        if self._level == "project":
            for sub in self._path_to_upload.iterdir():
                if not sub.is_dir():
                    continue
                for exp in sub.iterdir():
                    if exp.is_dir():
                        experiment.append(exp)
        elif self._level == "subject":
            for exp in self._path_to_upload.iterdir():
                if exp.is_dir():
                    experiment.append(exp)
        elif self._level == "experiment":
            experiment = [self._path_to_upload]

        if not experiment:
            raise ValueError("No experiments found.")

        self._scan_to_upload = []

        for exp in experiment:
            for scan in exp.iterdir():
                if scan.is_dir() and any(
                        f.suffix.lower() in [".dcm", ".dicom"] and f.is_file()
                        for f in scan.iterdir()):
                    self._scan_to_upload.append(scan)

    def validate_scan(self):
        REQUIRED_TAGS = {
            (0x0008, 0x0016): "SOP Class UID",
            (0x0008, 0x0018): "SOP Instance UID",
            (0x0020, 0x000D): "Study Instance UID",
            (0x0020, 0x000E): "Series Instance UID",
            (0x0020, 0x0013): "Instance Number",
            (0x0008, 0x0060): "Modality",
            (0x0010, 0x0010): "Patient Name",
            (0x0010, 0x0020): "Patient ID",
        }
        MANUFACTURER_EXPECTED = "FUJIFILM VisualSonics"

        self.get_valid_scans()
        valid_dicom = [file for folder in self._scan_to_upload for file in
                       Path(folder).iterdir() if
                       file.is_file() and file.suffix.lower() in [".dcm",
                                                                  ".dicom"]
                       ]
        for dicom_scan in valid_dicom:
            ds = dcmread(dicom_scan)

            for tag, name in REQUIRED_TAGS.items():
                if tag not in ds:
                    print(f"Miss: {name} ({tag})")
                    return False

            manufacturer = ds.get((0x0008, 0x0070), "")

            for tag in [(0x0008, 0x0016), (0x0008, 0x0018), (0x0020, 0x000D),
                        (0x0020, 0x000E)]:
                elem = ds.get(tag)
                uid = elem.value if elem else ""

                name = REQUIRED_TAGS.get(tag, "UID")
                if not UID(uid).is_valid:
                    print(f"UID not valid: {name} = {uid}")
                    return False

        return True

    @property
    def path_to_upload(self) -> Path | None:
        return self._path_to_upload

    @path_to_upload.setter
    def path_to_upload(self, path_to_upload: str):
        p = Path(path_to_upload)
        if not p.is_dir():
            raise ValueError(f"'{p}' is not a valid folder.")
        self._path_to_upload = p

    @property
    def level(self) -> str | None:
        return self._level

    @property
    def scan_to_upload(self) -> list[Path]:
        return self._scan_to_upload

    @level.setter
    def level(self, level: str):
        self._level = level
