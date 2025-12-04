import base64
import io

import numpy as np
import pydicom
from PIL import Image
from pydicom import dcmread
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import UID, generate_uid, ExplicitVRLittleEndian


class DicomService:
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

    @staticmethod
    def is_valid_dicom_file(dicom_file):
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

        ds = dcmread(dicom_file)

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

    @staticmethod
    def get_compatible_dicom_file(dicom_file):
        ds = dcmread(dicom_file)
        manufacturer = getattr(ds, "Manufacturer", "")

        if manufacturer == "FUJIFILM VisualSonics, Inc.":
            return DicomService._compatible_fujifilm(ds, dicom_file)
        else:
            return DicomService._compatible_ivis(ds, dicom_file)

    @staticmethod
    def _compatible_fujifilm(ds, dicom_file):
        if not hasattr(ds, 'file_meta') or ds.file_meta is None:
            ds.file_meta = FileMetaDataset()

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

    @staticmethod
    def dicom_to_base64(dicom_path: str):
        try:
            dicom = pydicom.dcmread(dicom_path)
            pixels = dicom.pixel_array.astype(np.float32)

            # Gestione MONOCHROME1
            if dicom.PhotometricInterpretation == "MONOCHROME1":
                pixels = pixels.max() - pixels

            # Normalizzazione
            pixels -= pixels.min()
            if pixels.max() != 0:
                pixels /= pixels.max()
            pixels *= 255
            pixels = pixels.astype(np.uint8)

            # Conversione in immagine
            if len(pixels.shape) == 2:
                img = Image.fromarray(pixels, mode="L")
            else:
                img = Image.fromarray(pixels)

            img.thumbnail((512, 512))

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode()

        except Exception as e:
            raise ValueError(f"DICOM conversion error: {e}")

    @staticmethod
    def read_DICOM_tags(dicom_path):
        try:
            ds = pydicom.dcmread(dicom_path, stop_before_pixels=True)
            elements = []

            for elem in ds:
                if elem.tag == (0x7FE0, 0x0010):  # Salta pixel data
                    continue

                tag_tuple = (elem.tag.group, elem.tag.elem)

                if tag_tuple in DicomParser.CEST_PRIVATE_TAGS:
                    name = DicomParser.CEST_PRIVATE_TAGS[tag_tuple]
                elif elem.name.startswith("Private tag"):
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