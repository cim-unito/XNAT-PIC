import base64
import io

import numpy as np
import pydicom
from PIL import Image


class DicomPreviewService:
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