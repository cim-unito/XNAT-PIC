import pydicom
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
        (0x1061, 0x1015): "Saturation offset (ppm)"
    }

    @staticmethod
    def _safe_string(value, max_length=200):
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
    def _tag_name(dataset, elem):
        tag_tuple = (elem.tag.group, elem.tag.elem)

        if tag_tuple in DicomTagReaderService.CEST_PRIVATE_TAGS:
            return DicomTagReaderService.CEST_PRIVATE_TAGS[tag_tuple]

        if elem.tag.is_private:
            creator = getattr(elem, "private_creator", None)
            creator_label = f"{creator}: " if creator else ""
            return f"{creator_label}{elem.name}"

        return elem.name

    @staticmethod
    def _process_dataset(dataset, elements, parent_path=""):
        for elem in dataset:
            if elem.tag == Tag(0x7FE0, 0x0010):
                continue

            tag_tuple = (elem.tag.group, elem.tag.elem)
            name = DicomTagReaderService._tag_name(dataset, elem)
            path = f"{parent_path}{name}" if not parent_path else f"{parent_path}/{name}"

            if elem.VR == "SQ":
                elements.append({
                    "tag": tag_tuple,
                    "name": name,
                    "value": f"Sequence of {len(elem.value)} item(s)",
                    "path": path
                })
                for index, item in enumerate(elem.value):
                    DicomTagReaderService._process_dataset(item, elements, f"{path}[{index}]")
            else:
                elements.append({
                    "tag": tag_tuple,
                    "name": name,
                    "value": DicomTagReaderService._safe_string(elem.value),
                    "path": path
                })

    @staticmethod
    def read_dicom_tags(dicom_path):
        try:
            dataset = pydicom.dcmread(dicom_path, stop_before_pixels=True, force=True)
            elements = []
            DicomTagReaderService._process_dataset(dataset, elements)
            return elements

        except Exception as error:
            raise ValueError(f"DICOM tag reading error: {error}")