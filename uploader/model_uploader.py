import base64
import io
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

from xnat_client.xnat_session import XnatSession


class ModelUploader:
    def __init__(self):
        self._path_to_upload: Path | None = None
        self._level: str | None = None
        self._scan_to_upload: list[Path] = []

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

    def dicom_to_base64(self, dicom_path: str) -> str:
        try:
            dicom = pydicom.dcmread(dicom_path)
            pixels = dicom.pixel_array.astype(np.float32)

            if dicom.PhotometricInterpretation == "MONOCHROME1":
                pixels = pixels.max() - pixels

            pixels -= pixels.min()
            if pixels.max() != 0:
                pixels /= pixels.max()
            pixels *= 255
            pixels = pixels.astype(np.uint8)

            if len(pixels.shape) == 2:
                img = Image.fromarray(pixels, mode="L")
            elif len(pixels.shape) == 3:
                img = Image.fromarray(pixels)
            else:
                raise ValueError("Unsupported DICOM format")

            img.thumbnail((512, 512))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode()
        except Exception as e:
            raise ValueError(f"DICOM conversion error: {e}")

    def read_dicom_tags(self, dicom_path: str) -> list[dict]:
        CEST_PRIVATE_TAGS = {
            (0x1061, 0x0010): "Creator of the parameter set",
            (0x1061, 0x1001): "Chemical Exchange Saturation Method",
            (0x1061, 0x1002): "Saturation type",
            (0x1061, 0x1003): "Pulse shape",
            (0x1061, 0x1004): "B1 saturation",
            (0x1061, 0x1005): "Pulse length",
            (0x1061, 0x1006): "Pulse number",
            (0x1061, 0x1007): "Interpulse delay",
            (0x1061, 0x1008): "Saturation length (ms)",
            (0x1061, 0x1009): "Readout time (ms)",
            (0x1061, 0x1010): "Pulse length 2 (ms)",
            (0x1061, 0x1011): "Duty cycle",
            (0x1061, 0x1012): "Recovery time (ms)",
            (0x1061, 0x1013): "Measurement number",
            (0x1061, 0x1014): "Saturation offset (Hz)",
            (0x1061, 0x1015): "Saturation offset (ppm)"
        }
        try:
            ds = pydicom.dcmread(dicom_path, stop_before_pixels=True)
            elements = []

            for elem in ds:
                if elem.tag == (0x7FE0, 0x0010):  # Skip PixelData
                    continue

                tag_tuple = (elem.tag.group, elem.tag.elem)

                if tag_tuple in CEST_PRIVATE_TAGS:
                    name = CEST_PRIVATE_TAGS[tag_tuple]
                else:
                    if elem.name.startswith("Private tag"):
                        name = f"Unknown private tag {tag_tuple}"
                    else:
                        name = elem.name

                elements.append({
                    "tag": tag_tuple,
                    "name": name,
                    "value": str(elem.value)
                })

            return elements

        except Exception as e:
            raise ValueError(f"DICOM tag reading error: {e}")

    def get_valid_scans(self):
        if self._path_to_upload is None:
            raise ValueError("Upload path not set.")

        experiment: list[Path] = []

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

        self._scan_to_upload.clear()
        for exp in experiment:
            for scan in exp.iterdir():
                if scan.is_dir() and any(
                        f.suffix.lower() in [".dcm", ".dicom"] and f.is_file()
                        for f in scan.iterdir()):
                    self._scan_to_upload.append(scan)

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
