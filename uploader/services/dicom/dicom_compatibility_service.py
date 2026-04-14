import copy
import hashlib
import socket
import uuid

import numpy as np
from pydicom import dcmread
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.errors import InvalidDicomError
from pydicom.uid import generate_uid, UID, ExplicitVRLittleEndian, SecondaryCaptureImageStorage


class DicomCompatibilityService:
    @staticmethod
    def update_study_instance_uid_map(dicom_file, study_instance_uid_map):
        sub_exp = DicomCompatibilityService._get_sub_exp(dicom_file)

        if sub_exp not in study_instance_uid_map:
            study_instance_uid_map[sub_exp] = generate_uid()

        return study_instance_uid_map

    @staticmethod
    def get_compatible_dicom_file(dicom_file, exp_uid_map):
        try:
            ds = dcmread(dicom_file)
        except InvalidDicomError as e:
            raise RuntimeError(f"Invalid DICOM file: {dicom_file}") from e
        except OSError as e:
            raise RuntimeError(f"Unable to read DICOM file: {dicom_file}") from e

        try:
            ds.file_meta = DicomCompatibilityService._build_meta_file(ds)
        except Exception as e:
            raise RuntimeError("Error creating file meta information") from e

        manufacturer = str(getattr(ds, "Manufacturer", "")).strip()
        implementation_version_name = str(
            getattr(ds.file_meta, "ImplementationVersionName", "")
        ).strip()

        if manufacturer.lower() == "fujifilm visualsonics, inc.":
            return DicomCompatibilityService._compatible_fujifilm(ds, dicom_file, exp_uid_map)
        if implementation_version_name.lower() == "living image":
            return DicomCompatibilityService._compatible_ivis(ds, dicom_file, exp_uid_map)

        raise ValueError(
            "Unsupported DICOM vendor: "
            f"Manufacturer='{manufacturer}', "
            f"ImplementationVersionName='{implementation_version_name}'"
        )

    @staticmethod
    def _build_meta_file(ds):
        # File Meta Dataset
        if not hasattr(ds, "file_meta") or ds.file_meta is None:
            ds.file_meta = FileMetaDataset()

        # File Meta Information Group Length
        if (not hasattr(ds.file_meta, 'FileMetaInformationGroupLength') or
                ds.file_meta.FileMetaInformationGroupLength is None):
            ds.file_meta.FileMetaInformationGroupLength = 202

        # File Meta Information Version
        if (not hasattr(ds.file_meta, 'FileMetaInformationVersion') or
                ds.file_meta.FileMetaInformationVersion is None):
            ds.file_meta.FileMetaInformationVersion = b"\x00\x01"

        # Media Storage SOP Class UID
        if hasattr(ds.file_meta, "MediaStorageSOPClassUID") and \
                UID(ds.file_meta.MediaStorageSOPClassUID).is_valid:
            pass
        elif hasattr(ds, "SOPClassUID") and UID(ds.SOPClassUID).is_valid:
            ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        else:
            ds.file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage

        # Media Storage SOP Instance UID
        if hasattr(ds.file_meta, "MediaStorageSOPInstanceUID") and \
                UID(ds.file_meta.MediaStorageSOPInstanceUID).is_valid:
            pass
        elif hasattr(ds, "SOPInstanceUID") and UID(ds.SOPInstanceUID).is_valid:
            ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        else:
            new_uid = generate_uid()
            ds.file_meta.MediaStorageSOPInstanceUID = new_uid

        # Transfer Syntax UID
        if not hasattr(ds.file_meta, "TransferSyntaxUID") or \
                not UID(ds.file_meta.TransferSyntaxUID).is_valid:
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        # Implementation Class UID
        if not hasattr(ds.file_meta, "ImplementationClassUID") or \
                not UID(ds.file_meta.ImplementationClassUID).is_valid:
            ds.file_meta.ImplementationClassUID = DicomCompatibilityService._generate_implementation_uid()

        return ds.file_meta

    @staticmethod
    def _compatible_fujifilm(ds, dicom_file, exp_uid_map):
        sub_exp = DicomCompatibilityService._get_sub_exp(dicom_file)
        study_instance_uid = exp_uid_map.get(sub_exp)
        if not study_instance_uid:
            raise KeyError(f"Missing StudyInstanceUID mapping for key '{sub_exp}'")

        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
        ds.PatientID = sub_exp
        ds.StudyInstanceUID = study_instance_uid
        ds.SeriesInstanceUID = generate_uid()
        if not hasattr(ds, "Modality"):
            ds.Modality = "OT"

        # From multiframe to single frame
        results = []
        pixel_array = ds.pixel_array
        if pixel_array.ndim != 4:
            raise ValueError("Unsupported pixel array shape")
        n_frames = int(getattr(ds, "NumberOfFrames", 0))
        if n_frames <= 0:
            raise ValueError("Invalid NumberOfFrames in FUJIFILM dataset")
        if pixel_array.shape[0] != n_frames:
            raise ValueError("NumberOfFrames does not match pixel array")
        # Tag to remove
        tags_to_remove = [
            (0x0028, 0x0008),  # Number of Frames
            (0x0018, 0x1063),  # Frame Time
            (0x0008, 0x2144),  # Recommended Display Frame Rate
            (0x0028, 0x0009),  # Frame Increment Pointer
        ]
        for tag in tags_to_remove:
            if tag in ds:
                del ds[tag]

        for i in range(n_frames):
            new_ds = copy.deepcopy(ds)
            new_file_meta = copy.deepcopy(ds.file_meta)
            # Pixel data
            frame = pixel_array[i, :, :, :]
            new_ds.PixelData = frame.tobytes()
            new_ds.Rows, new_ds.Columns = frame.shape[:2]

            voxel_spacing = [float(x) for x in ds.PixelSpacing] + [1.0]

            # UIDs
            new_uid = generate_uid()
            new_ds.file_meta.MediaStorageSOPInstanceUID = new_uid
            new_ds.SOPInstanceUID = new_uid
            new_ds.FrameOfReferenceUID = new_uid
            new_ds.InstanceNumber = i + 1
            new_ds.AcquisitionNumber = i + 1

            # Position
            new_ds.ImagePositionPatient = [0, 0,
                                           i * voxel_spacing[2]]
            new_ds.SliceLocation = i * voxel_spacing[2]

            # Windowing
            min_pixel = int(np.min(frame))
            max_pixel = int(np.max(frame))
            new_ds.SmallestImagePixelValue = min_pixel
            new_ds.LargestImagePixelValue = max_pixel
            new_ds.WindowCenter = int((max_pixel + min_pixel) / 2)
            new_ds.WindowWidth = int(max_pixel - min_pixel)

            # Output filename
            filename = f"{dicom_file.stem}_frame_{i + 1:03}.dcm"
            new_file = FileDataset(filename_or_obj="",
                                   dataset=new_ds,
                                   file_meta=new_file_meta,
                                   preamble=b"\0" * 128)
            results.append((new_file, filename))

        return results

    @staticmethod
    def _compatible_ivis(ds, dicom_file, exp_uid_map):
        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID

        sub_exp = DicomCompatibilityService._get_sub_exp(dicom_file)
        study_instance_uid = exp_uid_map.get(sub_exp)
        if not study_instance_uid:
            raise KeyError(f"Missing StudyInstanceUID mapping for key '{sub_exp}'")
        ds.PatientID = sub_exp
        ds.StudyInstanceUID = study_instance_uid
        ds.SeriesInstanceUID = generate_uid()
        if not hasattr(ds, "Modality"):
            ds.Modality = "OT"
        ds.PlanarConfiguration = 0

        filename = f"{dicom_file.stem}.dcm"
        new_file = ds
        return [(new_file, filename)]

    @staticmethod
    def _generate_implementation_uid():
        # MAC-address of computer
        mac_address = uuid.getnode()

        # Hostname of computer
        hostname = socket.gethostname()

        # Combination of data in a string
        unique_string = f"{mac_address}-{hostname}"
        # use one way function so that you cant get actual information of the system
        hash_object = hashlib.sha256(unique_string.encode())
        hex_dig = hash_object.hexdigest()
        numeric_hash = int(hex_dig, 16)
        numeric_hash_str = str(numeric_hash)
        # additional information loss (only 64 digits)
        implementation_uid = numeric_hash_str[:64]

        return implementation_uid

    @staticmethod
    def _get_sub_exp(dicom_file):
        try:
            return dicom_file.parents[2].name + "_" + dicom_file.parents[1].name
        except IndexError as e:
            raise ValueError(
                f"Unexpected dicom path structure for file: {dicom_file}"
            ) from e