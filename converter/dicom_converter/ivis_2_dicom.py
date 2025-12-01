from pathlib import Path

import numpy as np
import pydicom
from PIL import Image
from pydicom import FileDataset
from pydicom.uid import UID, generate_uid, ExplicitVRLittleEndian


class Ivis2DicomConverter:

    @staticmethod
    def convert(src_dst):
        src = Path(src_dst[0])
        dst = Path(src_dst[1])

        files = [
            f for f in src.iterdir()
            if f.is_file() and f.suffix.lower() == ".png" and "_SEQ" in f.name
        ]

        img = Image.open(files[0]).convert("RGB")
        pixel_array = np.asarray(img)

        pixel_bytes = pixel_array.tobytes()

        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = UID(
            "1.2.840.10008.5.1.4.1.1.7.4")
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        ds = FileDataset(dst, {}, file_meta=file_meta,
                         preamble=b"\0" * 128)

        parents = list(dst.parents)
        ds.PatientID = str(parents[1].name) + "_" + str(
            parents[0].name)
        ds.Modality = "OI"

        # --- 4. Metadata immagine RGB ---
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.PlanarConfiguration = 0  # RGB interleaved (R G B R G B ...)
        ds.Rows = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]

        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0

        ds.PixelData = pixel_bytes
        filename = dst / f"OI_1.dcm"
        filename.parent.mkdir(parents=True, exist_ok=True)
        ds.save_as(filename)