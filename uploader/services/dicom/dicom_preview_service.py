import base64
import io
from typing import Any

import numpy as np
import pydicom
from PIL import Image
from pydicom.pixel_data_handlers.util import (
    apply_modality_lut,
    apply_voi_lut,
    convert_color_space,
)


class DicomPreviewService:
    @staticmethod
    def dicom_to_base64(dicom_path: str):
        """Convert a DICOM file into a Base64-encoded PNG preview."""
        try:
            dicom = pydicom.dcmread(dicom_path)
            interpretation = dicom.get("PhotometricInterpretation", "").upper()
            pixels = dicom.pixel_array

            n_frames = int(getattr(dicom, "NumberOfFrames", 1))
            if n_frames > 1 and pixels.ndim > 2:
                frame_index = n_frames // 2
                pixels = pixels[frame_index]

            #pixels = DicomPreviewService._apply_modality_lut_safe(pixels, dicom)
            planar_config = int(getattr(dicom, "PlanarConfiguration", 0))
            voi_applied = False

            if (interpretation.startswith("MONOCHROME") or not interpretation) and DicomPreviewService._has_voi_info(
                dicom
            ):
                pixels = DicomPreviewService._apply_voi_lut_safe(pixels, dicom)
                voi_applied = True

            if interpretation.startswith("YBR") or interpretation == "PALETTE COLOR":
                try:
                    pixels = convert_color_space(pixels, interpretation or "RGB", "RGB")
                    interpretation = "RGB"
                    planar_config = 0
                except Exception as e:
                    print(f"DICOM conversion error: {e}")
                    pass

            if interpretation == "MONOCHROME1":
                pixels = pixels.max() - pixels

            if pixels.ndim == 3 and planar_config == 1 and pixels.shape[0] in (3, 4):
                pixels = np.moveaxis(pixels, 0, -1)

            pixels = DicomPreviewService._to_uint8_for_preview(pixels, voi_applied)

            if pixels.ndim == 2:
                img = Image.fromarray(pixels, mode="L")
            else:
                mode = "RGB" if pixels.shape[-1] == 3 else "RGBA" if pixels.shape[-1] == 4 else None
                img = Image.fromarray(pixels, mode=mode)

            img.thumbnail((256, 256))

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode()

        except Exception as e:
            raise ValueError(f"DICOM conversion error: {e}")

    @staticmethod
    def _apply_voi_lut_safe(pixels: np.ndarray, dicom: Any) -> np.ndarray:
        """Apply VOI LUT and fall back to raw pixels when unavailable."""
        try:
            return apply_voi_lut(pixels, dicom)
        except Exception as e:
            print(f"DICOM conversion error: {e}")
            return pixels

    @staticmethod
    def _apply_modality_lut_safe(pixels: np.ndarray, dicom: Any) -> np.ndarray:
        """Apply Modality LUT (Rescale Slope/Intercept) and fall back to raw pixels when unavailable."""
        try:
            return apply_modality_lut(pixels, dicom)
        except Exception as e:
            print(f"DICOM conversion error: {e}")
            return pixels

    @staticmethod
    def _has_voi_info(dicom: Any) -> bool:
        return bool(
            hasattr(dicom, "VOILUTSequence")
            or hasattr(dicom, "WindowCenter")
            or hasattr(dicom, "WindowWidth")
        )

    @staticmethod
    def _to_uint8_for_preview(pixels: np.ndarray, voi_applied: bool) -> np.ndarray:
        pixels = np.nan_to_num(pixels, nan=0.0, posinf=0.0, neginf=0.0)
        if pixels.dtype == np.uint8:
            return pixels

        pixels = pixels.astype(np.float32, copy=False)

        if voi_applied:
            # Preserve DICOM windowing output as much as possible.
            min_val = float(pixels.min())
            max_val = float(pixels.max())
            if min_val >= 0.0 and max_val <= 255.0:
                return pixels.clip(0, 255).astype(np.uint8, copy=False)

        # Robust fallback for preview when no reliable VOI info is present.
        lo = float(np.percentile(pixels, 1))
        hi = float(np.percentile(pixels, 99))
        if hi <= lo:
            lo = float(pixels.min())
            hi = float(pixels.max())
        if hi > lo:
            pixels = np.clip(pixels, lo, hi)
            pixels = (pixels - lo) / (hi - lo)
            pixels = (pixels * 255.0).clip(0, 255)
        else:
            pixels = np.zeros_like(pixels, dtype=np.float32)

        return pixels.astype(np.uint8, copy=False)