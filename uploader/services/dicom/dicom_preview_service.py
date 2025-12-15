import base64
import io

import numpy as np
import pydicom
from PIL import Image
from pydicom.pixel_data_handlers.util import apply_voi_lut, convert_color_space


class DicomPreviewService:
    @staticmethod
    def dicom_to_base64(dicom_path: str):
        try:
            dicom = pydicom.dcmread(dicom_path)
            interpretation = dicom.get("PhotometricInterpretation", "").upper()
            pixels = dicom.pixel_array

            # Pick a representative frame before further processing to bound memory usage
            n_frames = int(getattr(dicom, "NumberOfFrames", 1))
            if n_frames > 1 and pixels.ndim > 2:
                frame_index = n_frames // 2
                pixels = pixels[frame_index]

            planar_config = int(getattr(dicom, "PlanarConfiguration", 0))

            if interpretation.startswith("MONOCHROME") or not interpretation:
                pixels = DicomPreviewService._apply_voi_lut_safe(pixels, dicom)

            if interpretation.startswith("YBR") or interpretation == "PALETTE COLOR":
                try:
                    pixels = convert_color_space(pixels, interpretation or "RGB", "RGB")
                    interpretation = "RGB"
                    planar_config = 0
                except Exception:
                    # Fall back to raw pixels if color conversion fails
                    pass

            if interpretation == "MONOCHROME1":
                pixels = pixels.max() - pixels

            if pixels.ndim == 3 and planar_config == 1 and pixels.shape[0] in (3, 4):
                pixels = np.moveaxis(pixels, 0, -1)

            pixels = pixels.astype(np.float32, copy=False)
            min_val = float(pixels.min())
            max_val = float(pixels.max())

            if max_val > min_val:
                pixels = (pixels - min_val) / (max_val - min_val)
                pixels = (pixels * 255).clip(0, 255)
            else:
                pixels = np.zeros_like(pixels, dtype=np.float32)

            pixels = pixels.astype(np.uint8, copy=False)

            if pixels.ndim == 2:
                img = Image.fromarray(pixels, mode="L")
            else:
                mode = "RGB" if pixels.shape[-1] == 3 else "RGBA" if pixels.shape[-1] == 4 else None
                img = Image.fromarray(pixels, mode=mode)

            img.thumbnail((512, 512))

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode()

        except Exception as e:
            raise ValueError(f"DICOM conversion error: {e}")

    @staticmethod
    def _apply_voi_lut_safe(pixels, dicom):
        try:
            return apply_voi_lut(pixels, dicom)
        except Exception:
            return pixels