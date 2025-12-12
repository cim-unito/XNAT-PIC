from pathlib import Path

import numpy as np
from PIL import Image
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import SecondaryCaptureImageStorage, generate_uid, \
    ExplicitVRLittleEndian, PYDICOM_IMPLEMENTATION_UID

from converter.dicom_converter.ivis_2_dicom.ivis_metadata_parser import \
    IvisMetadataParser


class IvisDicomGenerator:
    def __init__(self, metadata_parse: IvisMetadataParser):
        self._metadata_parse = metadata_parse

    def generate_dicom(self, dst):
        image_list = self._metadata_parse.images
        study_instance_uid = generate_uid()
        for ind, image in enumerate(image_list):
            file_meta = self._build_meta_file()
            ds = self._build_dataset(file_meta, study_instance_uid)
            ds.PatientName = "IVIS_SUBJECT"
            ds.PatientID = "IVIS001"
            ds.InstanceNumber = ind

            img = self._load_image(image.file_path)
            ds = self._set_photometric_interpretation(img, ds)
            ds = self._set_bits_allocated(img, ds)
            ds = self._set_windowing_configuration(img, ds)
            ds.PixelData = img.tobytes()

            out_path = dst / Path(image.filename).with_suffix(".dcm")
            self._write_dicom(out_path, ds)

    def _build_meta_file(self):
        # --- File Meta Dataset ---
        file_meta = FileMetaDataset()

        # --- Media Storage SOP Class UID ---
        file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage

        # --- Media Storage SOP Instance UID ---
        new_uid = generate_uid()
        file_meta.MediaStorageSOPInstanceUID = new_uid

        # --- Transfer Syntax UID ---
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        # --- Implementation Class UID ---
        file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID

        return file_meta

    def _build_dataset(self, file_meta, study_instance_uid):
        ds = FileDataset(filename_or_obj="",
                         dataset={},
                         file_meta=file_meta,
                         preamble=b"\0" * 128)

        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.Modality = "OI"
        ds.ImageType = ["DERIVED", "SECONDARY", "OTHER"]
        ds.StudyInstanceUID = study_instance_uid
        ds.SeriesInstanceUID = generate_uid()
        ds.SeriesNumber = 1


        return ds

    def _load_image(self, path):
        img = Image.open(path)
        np_img = np.array(img)

        return np_img

    def _set_photometric_interpretation(self, img, ds):
        if img.ndim == 2:
            # ---- MONOCHROME ----
            rows, cols = img.shape
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"

        elif img.ndim == 3 and img.shape[2] == 3:
            # ---- RGB ----
            rows, cols, _ = img.shape
            ds.SamplesPerPixel = 3
            ds.PhotometricInterpretation = "RGB"
            ds.PlanarConfiguration = 0  # RGBRGBRGB

        else:
            raise ValueError("Formato immagine non supportato")

        ds.Rows = rows
        ds.Columns = cols

        return ds

    def _set_bits_allocated(self, img, ds):
        if img.dtype == np.uint8:
            ds.BitsAllocated = 8
            ds.BitsStored = 8
            ds.HighBit = 7
            ds.PixelRepresentation = 0
        elif img.dtype == np.uint16:
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0
        else:
            raise ValueError("Tipo pixel non supportato")

        return ds

    def _set_windowing_configuration(self, img, ds):
        vmin = int(img.min())
        vmax = int(img.max())
        ds.SmallestImagePixelValue = vmin
        ds.LargestImagePixelValue = vmax

        if vmin == vmax:
            window_center = vmin
            window_width = 1
        else:
            window_center = int((vmin + vmax) / 2.0)
            window_width = int((vmax - vmin))

        ds.WindowCenter = str(window_center)
        ds.WindowWidth = str(window_width)

        return ds

    def _write_dicom(self, out_path, ds):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.save_as(out_path, write_like_original=False)
        print(f"[OK] Saved: {out_path}")