import numpy as np
from pydicom import dcmread
from pydicom.dataset import FileMetaDataset
from pydicom.uid import generate_uid, UID, ExplicitVRLittleEndian


class DicomCompatibilityService:
    @staticmethod
    def update_study_instance_uid_map(dicom_file, study_instance_uid_map):
        exp = dicom_file.parents[2].name + "_" + dicom_file.parents[1].name

        if exp not in study_instance_uid_map:
            study_instance_uid_map[exp] = generate_uid()

        return study_instance_uid_map

    @staticmethod
    def get_compatible_dicom_file(dicom_file, exp_uid_map):
        ds = dcmread(dicom_file)

        if not hasattr(ds, 'file_meta') or ds.file_meta is None:
            print("File meta doesn't exist")
            return

        if (not hasattr(ds.file_meta, 'FileMetaInformationVersion') or
                ds.file_meta.FileMetaInformationVersion is None):
            ds.file_meta.FileMetaInformationVersion = b"\x00\x01"

        uid = UID(ds.SOPClassUID)
        print(uid.is_valid)

        manufacturer = getattr(ds, "Manufacturer", "")
        ImplementationVersionName = getattr(meta, "ImplementationVersionName", "")

        if manufacturer == "FUJIFILM VisualSonics, Inc.":
            return DicomCompatibilityService._compatible_fujifilm(ds,
                                                                  dicom_file)
        else:
            return DicomCompatibilityService._compatible_ivis(ds, dicom_file)

    @staticmethod
    def _compatible_fujifilm(ds, dicom_file):


        ds.file_meta.MediaStorageSOPClassUID = UID(
            "1.2.840.10008.5.1.4.1.1.6.1")

        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID

        # Tag
        parents = list(dicom_file.parents)
        ds.PatientID = str(parents[2].name) + "_" + str(parents[1].name)
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
            # file_meta = new_ds.file_meta
            # output_dicom = upload_path_xnat / dicom_scan.relative_to(
            #     self._path_to_upload)
            # base_name = output_dicom.stem
            # output_dicom = output_dicom.parent
            # filename = output_dicom / f"{base_name}_frame_{i + 1:03}.dcm"
            # filename.parent.mkdir(parents=True, exist_ok=True)
            # new_file = FileDataset(str(filename), new_ds,
            #                        file_meta=file_meta,
            #                        preamble=b"\0" * 128)
            # new_file.save_as(str(filename))

    @staticmethod
    def _compatible_ivis(ds, dicom_file):
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
        parents = list(dicom_file.parents)
        ds.PatientID = str(parents[2].name) + "_" + str(
            parents[1].name)
        ds.PlanarConfiguration = 0

        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()

        # -----------------------
        # FINAL SAVE
        # -----------------------
        # output_dicom = upload_path_xnat / dicom_scan.relative_to(
        #     self._path_to_upload)
        # output_dicom.parent.mkdir(parents=True, exist_ok=True)
        # ds.save_as(output_dicom, write_like_original=False)
        # print("DICOM saved in:", output_dicom)