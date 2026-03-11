from typing import Any

import pydicom
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset
from pydicom.multival import MultiValue
from pydicom.tag import Tag


class DicomTagReaderService:

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
        (0x1061, 0x1015): "Saturation offset (ppm)",
    }

    IVIS_PRIVATE_TAGS = {
        (0x0011, 0x1001): "Binning Factor",
        (0x0011, 0x1002): "f Number",
        (0x0011, 0x1003): "Field of View",
        (0x0011, 0x1004): "Filter Position",
        (0x0011, 0x1005): "Emission filter",
        (0x0011, 0x1006): "Exposure Time Sec",
        (0x0011, 0x1007): "Read Bias Level",
        (0x0011, 0x1008): "Demand Temperature",
        (0x0011, 0x1009): "Measured Temperature",
        (0x0011, 0x1010): "Data Multiplier",
        (0x0011, 0x1011): "Background Exposure (Seconds)",
        (0x0011, 0x1012): "Luminescent Exposure (Seconds)",
        (0x0011, 0x1013): "Luminescent Exposure Units",
        (0x0011, 0x1014): "Excitation filter",
    }

    @staticmethod
    def read_dicom_tags(dicom_path: str) -> list[dict[str, Any]]:
        """Read tags from a DICOM file and return them as a flat list."""
        try:
            dataset = pydicom.dcmread(dicom_path, stop_before_pixels=True, force=True)
            elements = []
            DicomTagReaderService._process_dataset(dataset, elements)
            return elements
        except Exception as error:
            raise ValueError(f"DICOM tag reading error: {error}")

    @staticmethod
    def _process_dataset(
        dataset: Dataset,
        elements: list[dict[str, Any]],
        parent_path: str = "",
    ) -> None:
        """Walk a DICOM dataset recursively and append flattened tag entries."""
        for elem in dataset:
            if elem.tag == Tag(0x7FE0, 0x0010):
                continue

            tag_tuple = DicomTagReaderService._tag_to_tuple(elem)
            name = DicomTagReaderService._tag_name(elem)
            path = f"{parent_path}{name}" if not parent_path else f"{parent_path}/{name}"

            if elem.VR == "SQ":
                elements.append(
                    {
                        "tag": tag_tuple,
                        "name": name,
                        "value": f"Sequence of {len(elem.value)} item(s)",
                        "path": path,
                    }
                )
                for index, item in enumerate(elem.value):
                    DicomTagReaderService._process_dataset(item, elements, f"{path}[{index}]")
            else:
                elements.append(
                    {
                        "tag": tag_tuple,
                        "name": name,
                        "value": DicomTagReaderService._safe_string(elem.value),
                        "path": path,
                    }
                )

    @staticmethod
    def _safe_string(value: Any, max_length: int = 200) -> str:
        """Convert a DICOM tag value to a compact, printable string."""
        if value is None:
            return ""

        if isinstance(value, bytes):
            preview = value[:64].hex()
            suffix = "..." if len(value) > 64 else ""
            return f"0x{preview}{suffix} ({len(value)} bytes)"

        if isinstance(value, MultiValue):
            joined = ", ".join(DicomTagReaderService._safe_string(v, max_length) for v in value[:8])
            if len(value) > 8:
                joined += ", ..."
            return f"[{joined}]"

        value_str = str(value)
        if len(value_str) > max_length:
            return f"{value_str[:max_length]}..."
        return value_str

    @staticmethod
    def _tag_to_tuple(elem: DataElement) -> tuple[int, int]:
        """Return `(group, element)` from a DICOM tag without relying on stub-specific attrs."""
        tag_value = int(elem.tag)
        return tag_value >> 16, tag_value & 0xFFFF

    @staticmethod
    def _tag_name(elem: DataElement) -> str:
        """Resolve a display name for a DICOM tag."""
        tag_tuple = DicomTagReaderService._tag_to_tuple(elem)

        if tag_tuple in DicomTagReaderService.CEST_PRIVATE_TAGS:
            return DicomTagReaderService.CEST_PRIVATE_TAGS[tag_tuple]

        if tag_tuple in DicomTagReaderService.IVIS_PRIVATE_TAGS:
            return DicomTagReaderService.IVIS_PRIVATE_TAGS[tag_tuple]

        tag_value = int(elem.tag)
        is_private = (tag_value >> 16) % 2 == 1
        if is_private:
            creator = getattr(elem, "private_creator", None)
            creator_label = f"{creator}: " if creator else ""
            return f"{creator_label}{elem.name}"

        return elem.name
