import copy

import numpy as np
from pydicom import dcmread
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import generate_uid, UID, ExplicitVRLittleEndian, \
    ImplicitVRLittleEndian, SecondaryCaptureImageStorage, \
    PYDICOM_IMPLEMENTATION_UID


class DicomCompatibilityService:
    @staticmethod
    def update_study_instance_uid_map(dicom_file, study_instance_uid_map):
        sub_exp = dicom_file.parents[2].name + "_" + dicom_file.parents[1].name

        if sub_exp not in study_instance_uid_map:
            study_instance_uid_map[sub_exp] = generate_uid()

        return study_instance_uid_map

    @staticmethod
    def get_compatible_dicom_file(dicom_file, exp_uid_map):
        ds = dcmread(dicom_file)

        ds.file_meta = DicomCompatibilityService._build_meta_file(ds)

        manufacturer = getattr(ds, "Manufacturer", "")
        implementation_version_name = getattr(ds.file_meta,
                                              "ImplementationVersionName", "")

        if manufacturer == "FUJIFILM VisualSonics, Inc.":
            return DicomCompatibilityService._compatible_fujifilm(ds,
                                                                  dicom_file,
                                                                  exp_uid_map)
        elif implementation_version_name == "Living Image":
            return DicomCompatibilityService._compatible_ivis(ds, dicom_file,
                                                              exp_uid_map)
        else:
            print("It is not a dicom file from ivis or fujifilm")
            return None

    @staticmethod
    def _build_meta_file(ds):
        # --- File Meta Dataset ---
        if not hasattr(ds, "file_meta") or ds.file_meta is None:
            ds.file_meta = FileMetaDataset()

        # --- File Meta Information Version---
        if (not hasattr(ds.file_meta, 'FileMetaInformationVersion') or
                ds.file_meta.FileMetaInformationVersion is None):
            ds.file_meta.FileMetaInformationVersion = b"\x00\x01"

        # --- Media Storage SOP Class UID ---
        if hasattr(ds.file_meta, "MediaStorageSOPClassUID") and \
                UID(ds.file_meta.MediaStorageSOPClassUID).is_valid:
            pass
        elif hasattr(ds, "SOPClassUID") and UID(ds.SOPClassUID).is_valid:
            ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        else:
            ds.file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage

        # --- Media Storage SOP Instance UID ---
        if hasattr(ds.file_meta, "MediaStorageSOPInstanceUID") and \
                UID(ds.file_meta.MediaStorageSOPInstanceUID).is_valid:
            pass
        elif hasattr(ds, "SOPInstanceUID") and UID(ds.SOPInstanceUID).is_valid:
            ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        else:
            new_uid = generate_uid()
            ds.file_meta.MediaStorageSOPInstanceUID = new_uid

        # --- Transfer Syntax UID ---
        if not hasattr(ds.file_meta, "TransferSyntaxUID") or \
                not UID(ds.file_meta.TransferSyntaxUID).is_valid:
            ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

        # --- Implementation Class UID ---
        if not hasattr(ds.file_meta, "ImplementationClassUID") or \
                not UID(ds.file_meta.ImplementationClassUID).is_valid:
            ds.file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID

        return ds.file_meta

    @staticmethod
    def _compatible_fujifilm(ds, dicom_file, exp_uid_map):
        sub_exp = dicom_file.parents[2].name + "_" + dicom_file.parents[1].name

        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
        ds.PatientID = sub_exp
        ds.StudyInstanceUID = exp_uid_map.get(sub_exp)
        ds.SeriesInstanceUID = generate_uid()
        if not hasattr(ds, "Modality"):
            ds.Modality = "OT"

        # --- From multiframe to single frame ---
        results = []
        pixel_array = ds.pixel_array
        if pixel_array.ndim != 4:
            raise ValueError("Unsupported pixel array shape")
        n_frames = int(ds.NumberOfFrames)
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

        sub_exp = dicom_file.parents[2].name + "_" + dicom_file.parents[1].name
        ds.PatientID = sub_exp
        ds.StudyInstanceUID = exp_uid_map.get(sub_exp)
        ds.SeriesInstanceUID = generate_uid()
        if not hasattr(ds, "Modality"):
            ds.Modality = "OT"
        ds.PlanarConfiguration = 0

        filename = f"{dicom_file.stem}.dcm"
        new_file = ds
        return [(new_file, filename)]