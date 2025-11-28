import shutil
from typing import List, Dict

from PIL import Image
import numpy as np
import pydicom
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import UID, generate_uid, ExplicitVRLittleEndian
from pathlib import Path

class ModelConverter:
    def __init__(self):
        self._path_to_convert: Path | None = None
        self._level: str | None = None
        self._conversion_type: str | None = None
        self._path_converted: Path | None = None
        self._scan_to_convert: list[Path] = []
        self._scan_converted: list[Path] = []

    @property
    def path_to_convert(self):
        return self._path_to_convert

    @path_to_convert.setter
    def path_to_convert(self, path_to_convert):
        p = Path(path_to_convert)
        if not p.is_dir():
            raise ValueError(f"'{p}' is not a valid folder.")
        self._path_to_convert = p

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    @property
    def conversion_type(self):
        return self._conversion_type

    @conversion_type.setter
    def conversion_type(self, conversion_type):
        self._conversion_type = conversion_type

    @property
    def path_converted(self):
        return self._path_converted

    @path_converted.setter
    def path_converted(self, path_to_convert: Path):
        p = path_to_convert
        self._path_converted = p.parent / (p.name + "_dcm")

    @property
    def scan_to_convert(self):
        return self._scan_to_convert

    @property
    def scan_converted(self):
        return self._scan_converted



    def get_destination_scans(self):
        if self._path_converted is None or self._path_to_convert is None:
            raise ValueError("Paths not set.")
        self._scan_converted = [
            self._path_converted / p.relative_to(self._path_to_convert)
            for p in self._scan_to_convert
        ]

    def ivis2dicom_converter(self, src_dst):
        src = Path(src_dst[0])
        dst = Path(src_dst[1])

        files = [
            f for f in src.iterdir()
            if f.is_file() and f.suffix.lower() == ".png" and "_SEQ" in f.name
        ]

        img = Image.open(files[0]).convert("RGB")
        pixel_array = np.asarray(img)

        pixel_bytes = pixel_array.tobytes()

        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = UID(
            "1.2.840.10008.5.1.4.1.1.7.4")
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        ds = FileDataset(dst, {}, file_meta=file_meta,
                         preamble=b"\0" * 128)

        parents = list(dst.parents)
        ds.PatientID = str(parents[1].name) + "_" + str(
            parents[0].name)
        ds.Modality = "OI"

        # --- 4. Metadata immagine RGB ---
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.PlanarConfiguration = 0  # RGB interleaved (R G B R G B ...)
        ds.Rows = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]

        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0

        ds.PixelData = pixel_bytes
        filename = dst / f"OI_1.dcm"
        filename.parent.mkdir(parents=True, exist_ok=True)
        ds.save_as(filename)



