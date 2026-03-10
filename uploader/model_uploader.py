from pathlib import Path

from uploader.services.dicom.dicom_compatibility_service import \
    DicomCompatibilityService
from uploader.services.dicom.dicom_modify_modality import DicomModifyModality
from uploader.services.dicom.dicom_validator_service import \
    DicomValidatorService
from uploader.services.filesystem.filesystem_service import FilesystemService


class ModelUploader:
    def __init__(self):
        self._input_root = None
        self._level = None
        self._tmp_folder_to_upload = None

    def reset_level(self):
        self._level = None


    def validate_dicom_files(self):
        if self._level and self._level.value == "file":
            self._tmp_folder_to_upload = self._input_root
            return
        list_dicom_files = FilesystemService.get_list_dicom_files(
            self._input_root, self._level)

        if not list_dicom_files:
            print(
                f"The folder {self._input_root} does not contain dicom files)")
            return

        tmp_dir = FilesystemService.create_temp_dicom_upload_directory()
        self._tmp_folder_to_upload = tmp_dir / self._input_root.name

        study_instance_uid_map = {}
        for dicom_file in list_dicom_files:
            if DicomValidatorService.is_valid_dicom_file(dicom_file):
                FilesystemService.copy_dicom_file(self._input_root, dicom_file,
                                                  self._tmp_folder_to_upload)
            else:
                exp_uid_map = DicomCompatibilityService.update_study_instance_uid_map(
                    dicom_file, study_instance_uid_map)
                new_dicom_file = DicomCompatibilityService.get_compatible_dicom_file(
                    dicom_file, exp_uid_map)
                if new_dicom_file:
                    FilesystemService.save_dicom_file(self._input_root,
                                                      dicom_file,
                                                      self._tmp_folder_to_upload,
                                                      new_dicom_file)

    def modify_modality(self, dicom_path, new_modality):
        dicom_files_to_modify = []

        if dicom_path.is_file():
            if dicom_path.suffix.lower() in [".dcm", ".dicom"]:
                dicom_files_to_modify.append(dicom_path)
            else:
                raise ValueError("It is not a dicom file (.dcm o .dicom)")

        elif dicom_path.is_dir():
            dicom_files_to_modify = list(dicom_path.rglob("*.dcm")) + list(
                dicom_path.rglob("*.dicom"))

            if not dicom_files_to_modify:
                raise ValueError("Folder does not contain dicom file")

        else:
            raise ValueError("Path does not exist")

        DicomModifyModality.modify_modality(dicom_files_to_modify, new_modality)

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

    @property
    def tmp_folder_to_upload(self):
        return self._tmp_folder_to_upload

    @tmp_folder_to_upload.setter
    def tmp_folder_to_upload(self, tmp_folder_to_upload):
        self._tmp_folder_to_upload = tmp_folder_to_upload
