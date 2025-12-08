from pydicom import dcmread
from pydicom.uid import UID


class DicomValidatorService:
    @staticmethod
    def is_valid_dicom_file(dicom_file):
        REQUIRED_TAGS = {
            (0x0008, 0x0016): "SOP Class UID",
            (0x0008, 0x0018): "SOP Instance UID",
            (0x0020, 0x000D): "Study Instance UID",
            (0x0020, 0x000E): "Series Instance UID",
            (0x0008, 0x0060): "Modality",
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
