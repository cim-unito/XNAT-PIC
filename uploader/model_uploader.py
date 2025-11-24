import base64
import io
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image
from pydicom import dcmread
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import UID, generate_uid, ExplicitVRLittleEndian


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
            experiment = [
                exp
                for sub in self._path_to_upload.iterdir() if sub.is_dir()
                for exp in sub.iterdir() if exp.is_dir()
            ]
        elif self._level == "subject":
            experiment = [exp for exp in self._path_to_upload.iterdir() if exp.is_dir()]

        elif self._level == "experiment":
            experiment = [self._path_to_upload]

        if not experiment:
            raise ValueError("No experiments found.")

        self._scan_to_upload = []

        self._scan_to_upload = [
            file
            for exp in experiment
            for scan in exp.iterdir() if scan.is_dir()
            for file in scan.iterdir()
            if file.is_file() and file.suffix.lower() in [".dcm", ".dicom"]
        ]

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

        self.get_valid_scans()

        for dicom_scan in self._scan_to_upload:
            ds = dcmread(dicom_scan)

            for tag, name in REQUIRED_TAGS.items():
                if tag not in ds:
                    print(f"Miss: {name} ({tag})")
                    return False

            for tag in [(0x0008, 0x0016), (0x0008, 0x0018), (0x0020, 0x000D),
                        (0x0020, 0x000E)]:
                elem = ds.get(tag)
                uid = elem.value if elem else ""

                name = REQUIRED_TAGS.get(tag, "UID")
                if not UID(uid).is_valid:
                    print(f"UID not valid: {name} = {uid}")
                    return False

        return True

    def create_xnat_folder(self, upload_path_xnat):
        if upload_path_xnat.exists() and upload_path_xnat.is_dir():
            print(
                f"The folder '{upload_path_xnat}' "
                f"already exists. Overwrite!"
            )
            shutil.rmtree(upload_path_xnat)
            upload_path_xnat.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Create the folder '{upload_path_xnat}'.")
            upload_path_xnat.mkdir(parents=True, exist_ok=True)

    def create_new_scan(self, upload_path_xnat):
        for dicom_scan in self._scan_to_upload:
            ds = dcmread(dicom_scan)
            manufacturer = getattr(ds, "Manufacturer", "")

            if manufacturer == "FUJIFILM VisualSonics, Inc.":
                if not hasattr(ds, 'file_meta') or ds.file_meta is None:
                    ds.file_meta = FileMetaDataset()

                ds.file_meta.MediaStorageSOPClassUID = UID(
                    "1.2.840.10008.5.1.4.1.1.6.1")

                ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID

                # Tag
                ds.PatientID = str(dicom_scan.parents[3].name)
                ds.StudyInstanceUID = generate_uid()
                ds.SeriesInstanceUID = generate_uid()

                ds.Modality = "OT"

                ###########################################################
                pixel_array = ds.pixel_array
                n_frame = int(ds.NumberOfFrames)

                for i in range(n_frame):
                    new_ds = ds.copy()

                    frame = pixel_array[i, :, :, :]

                    new_ds.PixelData = frame.tobytes()
                    new_ds.Rows, new_ds.Columns = frame.shape[:2]
                    voxel_spacing = [float(x) for x in ds.PixelSpacing] + [
                        1.0]  # [dx, dy, dz]

                    # tag to remove
                    tag_to_remove = [
                        (0x0028, 0x0008),
                        (0x0018, 0x1063),
                        (0x0008, 0x2144),
                        (0x0028, 0x0009),
                    ]

                    for tag in tag_to_remove:
                        if tag in new_ds:
                            del new_ds[tag]

                    # UID updated
                    new_uid = generate_uid()
                    new_ds.SOPInstanceUID = new_uid
                    new_ds.file_meta.MediaStorageSOPInstanceUID = new_uid
                    new_ds.FrameOfReferenceUID = generate_uid()

                    new_ds.InstanceNumber = i + 1
                    new_ds.AcquisitionNumber = i + 1
                    new_ds.ImagePositionPatient = [0, 0,
                                                   i * voxel_spacing[2]]
                    new_ds.SliceLocation = i * voxel_spacing[2]

                    min_pixel = int(np.min(frame))
                    max_pixel = int(np.max(frame))
                    new_ds.SmallestImagePixelValue = min_pixel
                    new_ds.LargestImagePixelValue = max_pixel
                    new_ds.WindowCenter = int((max_pixel + min_pixel) / 2)
                    new_ds.WindowWidth = int(max_pixel - min_pixel)

                    # Salva il file
                    file_meta = new_ds.file_meta
                    output_dicom = upload_path_xnat / dicom_scan.relative_to(
                        self._path_to_upload)
                    base_name = output_dicom.stem
                    output_dicom = output_dicom.parent
                    filename = output_dicom / f"{base_name}_frame_{i + 1:03}.dcm"
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    new_file = FileDataset(str(filename), new_ds,
                                           file_meta=file_meta,
                                           preamble=b"\0" * 128)
                    # new_file.is_little_endian = True
                    # new_file.is_implicit_VR = False
                    new_file.save_as(str(filename))
            else:
                ds.file_meta = FileMetaDataset()
                ds.file_meta.MediaStorageSOPClassUID = UID(
                    "1.2.840.10008.5.1.4.1.1.7.4")  # TrueColor Secondary Capture
                ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
                ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
                ds.file_meta.ImplementationClassUID = UID(
                    "1.2.276.0.7230010.3.0.3.6.7")

                # Required DICOM identifiers
                ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
                ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID

                # Modality
                ds.Modality = "OT"
                ds.PatientID = str(dicom_scan.parents[3].name)
                ds.PlanarConfiguration = 0

                ds.StudyInstanceUID = generate_uid()
                ds.SeriesInstanceUID = generate_uid()

                # -----------------------
                # FINAL SAVE
                # -----------------------
                output_dicom = upload_path_xnat / dicom_scan.relative_to(
                    self._path_to_upload)
                output_dicom.parent.mkdir(parents=True, exist_ok=True)
                ds.save_as(output_dicom, write_like_original=False)
                print("DICOM saved in:", output_dicom)

    def exist_ot_modality(self):
        self.get_valid_scans()

        for dicom_scan in self._scan_to_upload:
            ds = dcmread(dicom_scan)
            modality = getattr(ds, "Modality", "")

            if modality == "OT":
                return True
        return False

    def modify_modality(self, dicom_files, new_modality):
        print(dicom_files)
        print(new_modality)
        dirs = [Path(p) for p in dicom_files if Path(p).is_dir()]

        # 2) Tieni solo i leaf (percorsi non prefisso di altri)
        unique = []
        for p in dirs:
            if not any(
                    other != p and other.is_relative_to(p) for other in dirs):
                unique.append(Path(p))

        dicom_files_to_modify = [
            f
            for folder in unique
            for ext in ("*.dcm", "*.dicom")
            for f in folder.rglob(ext)
        ]
        print(dicom_files_to_modify)
        for dicom_scan in dicom_files_to_modify:
            ds = dcmread(dicom_scan)
            ds.Modality = new_modality
            dicom_scan.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(dicom_scan, write_like_original=False)

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
