from pydicom import dcmread


class DicomModifyModality:
    @staticmethod
    def modify_modality(dicom_files_to_modify, new_modality):
        for dicom_scan in dicom_files_to_modify:
            ds = dcmread(dicom_scan)
            ds.Modality = new_modality
            dicom_scan.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(dicom_scan, write_like_original=False)