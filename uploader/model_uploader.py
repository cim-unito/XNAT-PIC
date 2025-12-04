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

from uploader.services.dicom_service import DicomService
from uploader.services.filesystem_service import FilesystemService


class ModelUploader:
    def __init__(self):
        self._input_root = None
        self._level = None
        self._tmp_folder_to_upload = None

    def get_list_directory_treeview(self, path):
        return FilesystemService.get_list_directory_treeview(path)

    def validate_dicom_files(self):
        list_dicom_files = FilesystemService.get_list_dicom_files(
            self._input_root, self._level)

        if not list_dicom_files:
            print(
                f"The folder {self._input_root} does not contain dicom files)")
            return

        self._tmp_folder_to_upload = FilesystemService.create_temp_dicom_upload_directory()

        for dicom_file in list_dicom_files:
            if DicomService.is_valid_dicom_file(dicom_file):
                FilesystemService.copy_dicom_file(self._input_root, dicom_file,
                                                  self._tmp_folder_to_upload)
            else:
                new_dicom_file = DicomService.get_compatible_dicom_file(
                    dicom_file)
                if new_dicom_file:
                    pass
                    # FilesystemService.save_dicom_file(self._input_root,
                    #                                   dicom_file,
                    #                                   self._tmp_folder_to_upload)

    def modify_modality(self, dicom_files, new_modality):
        dirs = [Path(p) for p in dicom_files if Path(p).is_dir()]

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
        for dicom_scan in dicom_files_to_modify:
            ds = dcmread(dicom_scan)
            ds.Modality = new_modality
            dicom_scan.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(dicom_scan, write_like_original=False)

    @property
    def input_root(self):
        return self._input_root

    @input_root.setter
    def input_root(self, input_root):
        p = Path(input_root)
        if not p.is_dir():
            raise ValueError(f"'{p}' is not a valid folder.")
        self._input_root = p

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
