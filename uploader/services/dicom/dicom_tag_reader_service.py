import pydicom


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
    def read_dicom_tags(dicom_path):
        try:
            ds = pydicom.dcmread(dicom_path, stop_before_pixels=True)
            elements = []

            for elem in ds:
                if elem.tag == (0x7FE0, 0x0010):  # Salta pixel data
                    continue

                tag_tuple = (elem.tag.group, elem.tag.elem)

                if tag_tuple in DicomTagReaderService.CEST_PRIVATE_TAGS:
                    name = DicomTagReaderService.CEST_PRIVATE_TAGS[tag_tuple]
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