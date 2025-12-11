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

    def generate_dicom(self):
        image_list = self._metadata_parse.images
        results = []
        study_instance_uid = generate_uid()
        for image in image_list:
            np_img, samples_per_pixel = self._load_image(image.file_path)

            np_img_16 = self._convert_to_16bit(np_img)
            np_img_16 = np.ascontiguousarray(np_img_16)
            rows, cols = np_img_16.shape[:2]

            file_meta = self._build_meta_file()

            ds = FileDataset(filename_or_obj="",
                             dataset={},
                             file_meta=file_meta,
                             preamble=b"\0" * 128)

            ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
            ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
            ds.Modality = "OI"
            ds.ImageType = ["ORIGINAL", "PRIMARY"]
            ds.PatientName = "IVIS_SUBJECT"
            ds.PatientID = "IVIS001"
            ds.StudyInstanceUID = study_instance_uid
            ds.SeriesInstanceUID = generate_uid()
            ds.SeriesNumber = 1
            ds.InstanceNumber = 1
            ds.Rows = rows
            ds.Columns = cols

            ds.SamplesPerPixel = samples_per_pixel
            if samples_per_pixel == 1:
                ds.PhotometricInterpretation = "MONOCHROME2"
            else:
                ds.PhotometricInterpretation = "RGB"
                ds.PlanarConfiguration = 0  # RGB interleavato per pixel

            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0  # unsigned

            vmin = int(np_img_16.min())
            vmax = int(np_img_16.max())
            ds.SmallestImagePixelValue = vmin
            ds.LargestImagePixelValue = vmax

            if vmin == vmax:
                window_center = vmin
                window_width = 1
            else:
                window_center = (vmin + vmax) / 2.0
                window_width = (vmax - vmin)

            ds.WindowCenter = int(window_center)
            ds.WindowWidth = int(window_width)

            ds.PixelData = np_img_16.tobytes()

            ds.is_little_endian = True
            ds.is_implicit_VR = False

            p = Path(image.filename)
            filename = p.with_suffix(".dcm")

            results.append((ds, filename))
        return results

    def _load_image(self, path):
        img = Image.open(path)

        # Normalizza i modi più comuni
        if img.mode == "P":
            img = img.convert("RGB")
        elif img.mode in ("1",):
            img = img.convert("L")
        elif img.mode in ("LA",):
            img = img.convert("L")
        elif img.mode in ("RGBA", "CMYK"):
            img = img.convert("RGB")

        np_img = np.array(img)

        if np_img.ndim == 2:
            samples_per_pixel = 1
        elif np_img.ndim == 3 and np_img.shape[2] == 3:
            samples_per_pixel = 3
        else:
            raise ValueError(
                f"Formato TIFF non supportato: shape={np_img.shape}, mode={img.mode}")

        return np_img, samples_per_pixel

    def _convert_to_16bit(self, np_img):
        np_img = np.asarray(np_img)

        # --- BOOL (1-bit)
        if np.issubdtype(np_img.dtype, np.bool_):
            return (np_img.astype(np.uint16) * 65535)

        # --- INTEGER (signed o unsigned)
        if np.issubdtype(np_img.dtype, np.integer):

            # Caso ottimizzato: già uint16, range valido
            if np_img.dtype == np.uint16:
                return np_img.copy()

            # Convertiamo a float64 per evitare overflow
            img = np_img.astype(np.float64)

            vmin = img.min()
            vmax = img.max()

            # Range costante → immagine piatta
            if vmax == vmin:
                return np.zeros_like(np_img, dtype=np.uint16)

            # Normalizzazione a 0..1
            img_norm = (img - vmin) / (vmax - vmin)
            img_norm = np.clip(img_norm, 0.0, 1.0)

            return (img_norm * 65535.0).astype(np.uint16)

        # --- FLOATING POINT
        if np.issubdtype(np_img.dtype, np.floating):
            img = np_img.astype(np.float64)

            # Maschera dei valori finiti
            mask = np.isfinite(img)

            if not np.any(mask):
                raise ValueError(
                    "L'immagine float non contiene valori finiti.")

            vmin = img[mask].min()
            vmax = img[mask].max()

            if vmax == vmin:
                return np.zeros_like(np_img, dtype=np.uint16)

            # Normalizzazione solo sui valori validi
            img_norm = (img - vmin) / (vmax - vmin)
            img_norm = np.clip(img_norm, 0.0, 1.0)

            return (img_norm * 65535.0).astype(np.uint16)

        raise ValueError(f"Tipo pixel non supportato: {np_img.dtype}")

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
