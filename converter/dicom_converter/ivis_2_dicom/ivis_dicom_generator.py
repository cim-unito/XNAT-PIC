from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import SecondaryCaptureImageStorage, generate_uid, \
    ExplicitVRLittleEndian, PYDICOM_IMPLEMENTATION_UID

from converter.dicom_converter.ivis_2_dicom.ivis_metadata_parser import \
    IvisMetadata


class IvisDicomGenerator:
    def __init__(self, metadata_parse: IvisMetadata):
        self._metadata_parse = metadata_parse

    def generate_dicom(self, dst):
        image_list = self._metadata_parse.get_images()
        study_instance_uid = generate_uid()
        for ind, image in enumerate(image_list):
            file_meta = self._build_meta_file()
            ds = self._build_dataset(file_meta, study_instance_uid)
            ds.PatientName = "IVIS_SUBJECT"
            ds.PatientID = "IVIS001"
            # ds.InstanceNumber = ind

            img = self._load_image(image.file_path)
            ds = self._set_photometric_interpretation(img, ds)
            ds = self._set_bits_allocated(img, ds)
            ds = self._set_windowing_configuration(img, ds)
            ds.PixelData = img.tobytes()

            ds = self._set_section_tag(ds)

            if image.metadata:
                ds.add_new((0x0011, 0x0010), "LO", "IVIS_PERKINELMER")
                ds = self._set_image_tag(image, ds)

            out_path = dst / Path(image.filename).with_suffix(".dcm")
            self._write_dicom(out_path, ds)

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

    def _build_dataset(self, file_meta, study_instance_uid):
        ds = FileDataset(filename_or_obj="",
                         dataset={},
                         file_meta=file_meta,
                         preamble=b"\0" * 128)

        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.Modality = "OI"
        ds.ImageType = ["DERIVED", "SECONDARY", "OTHER"]
        ds.StudyInstanceUID = study_instance_uid
        ds.SeriesInstanceUID = generate_uid()
        ds.SeriesNumber = 1

        return ds

    def _load_image(self, path):
        img = Image.open(path)
        np_img = np.array(img)

        return np_img

    def _set_photometric_interpretation(self, img, ds):
        if img.ndim == 2:
            # ---- MONOCHROME ----
            rows, cols = img.shape
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"

        elif img.ndim == 3 and img.shape[2] == 3:
            # ---- RGB ----
            rows, cols, _ = img.shape
            ds.SamplesPerPixel = 3
            ds.PhotometricInterpretation = "RGB"
            ds.PlanarConfiguration = 0  # RGBRGBRGB

        else:
            raise ValueError("Formato immagine non supportato")

        ds.Rows = rows
        ds.Columns = cols

        return ds

    def _set_bits_allocated(self, img, ds):
        if img.dtype == np.uint8:
            ds.BitsAllocated = 8
            ds.BitsStored = 8
            ds.HighBit = 7
            ds.PixelRepresentation = 0
        elif img.dtype == np.uint16:
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0
        else:
            raise ValueError("Tipo pixel non supportato")

        return ds

    def _set_windowing_configuration(self, img, ds):
        vmin = int(img.min())
        vmax = int(img.max())
        ds.SmallestImagePixelValue = vmin
        ds.LargestImagePixelValue = vmax

        if vmin == vmax:
            window_center = vmin
            window_width = 1
        else:
            window_center = int((vmin + vmax) / 2.0)
            window_width = int((vmax - vmin))

        ds.WindowCenter = str(window_center)
        ds.WindowWidth = str(window_width)

        return ds

    def _set_section_tag(self, ds):
        sections_list = self._metadata_parse.get_sections()
        for section in sections_list:
            if section.name == "ClickNumber":
                ds.SoftwareVersions = self._stringify(
                    section.get_metadata_value(
                        "Living Image Version"))
                ds.InstanceNumber = int(self._stringify(
                    section.get_metadata_value(
                        "ClickNumber Index")))
            elif section.name == "User Label Name Set":
                ds.PatientID = self._stringify(
                    section.get_metadata_value(
                        "Animal Number"))
                ds.PatientSex = self._stringify(
                    section.get_metadata_value(
                        "Sex"))
                ds.PatientSpeciesDescription = self._stringify(
                    section.get_metadata_value(
                        "Animal Model"))
                ds.StrainDescription = self._stringify(
                    section.get_metadata_value(
                        "Animal Strain"))
                ds.StudyID = self._stringify(
                    section.get_metadata_value(
                        "Experiment"))
            elif section.name == "User Input":
                ds.OperatorsName = self._stringify(
                    section.get_metadata_value(
                        "User ID"))
                ds.InstitutionalDepartmentName = self._stringify(
                    section.get_metadata_value(
                        "Group"))
            elif section.name == "Analysis User Input":
                pass
            elif section.name == "Camera System Info":
                # System IVIS
                ds.DeviceSerialNumber = self._stringify(
                    section.get_metadata_value(
                        "Camera System ID"))
                ds.StationName = self._stringify(
                    section.get_metadata_value(
                        "Camera System alias"))
                ds.ManufacturerModelName = self._stringify(
                    section.get_metadata_value(
                        "System Configuration"))
                ds.Manufacturer = "PerkinElmer"

                # Camera/CCD
                ds.DetectorType = self._stringify(
                    section.get_metadata_value(
                        "Camera Type"))
                ds.DetectorID = self._stringify(
                    section.get_metadata_value(
                        "Camera CCD Type"))
            elif section.name == "Graph Controls":
                ds.RescaleSlope = float(self._stringify(
                    section.get_metadata_value(
                        "Calibration Value Per Count")))
                ds.RescaleIntercept = 0.0
                ds.RescaleType = self._stringify(
                    section.get_metadata_value(
                        "Intensity Calibration"))

                if int(self._stringify(
                        section.get_metadata_value(
                            "Reversed"))) == 1:
                    ds.PixelIntensityRelationship = "INVERSE"
                else:
                    ds.PixelIntensityRelationship = "LIN"

                ds.ImageRotation = int(self._stringify(
                    section.get_metadata_value(
                        "Rotation")))
        return ds

    def _set_image_tag(self, image, ds):
        ds.SeriesDescription = image.section

        self._set_acquisition_datetime(ds, image)

        # -------- COMMON ----------
        ds.add_new((0x0011, 0x1001), "US", int(
            self._stringify(image.get_metadata_value("Binning Factor")))
                   )

        # ========================================================
        if "photo" in image.section:
            ds.add_new((0x0011, 0x1002), "US", int(
                self._stringify(
                    image.get_metadata_value("f Number")))
                       )

            ds.add_new((0x0011, 0x1003), "DS",
                       self._stringify(
                           image.get_metadata_value("Field of View")))

            ds.add_new((0x0011, 0x1004), "US", int(
                self._stringify(
                    image.get_metadata_value("Filter Position")))
                       )

            ds.add_new((0x0011, 0x1005), "LO",
                       self._stringify(
                           image.get_metadata_value("Emission filter")))

            ds.add_new((0x0011, 0x1006), "DS",
                       self._stringify(
                           image.get_metadata_value("Exposure Time Sec")))

        # ========================================================
        elif "readbias" in image.section:
            ds.add_new((0x0011, 0x1007), "DS",
                       self._stringify(
                           image.get_metadata_value("Read Bias Level")))

            ds.add_new((0x0011, 0x1008), "DS",
                       self._stringify(
                           image.get_metadata_value("Demand Temperature")))

            ds.add_new((0x0011, 0x1009), "DS",
                       self._stringify(
                           image.get_metadata_value("Measured Temperature")))

            ds.add_new((0x0011, 0x1010), "US", int(
                self._stringify(
                    image.get_metadata_value("Data Multiplier")))
                       )

            ds.add_new((0x0011, 0x1011), "DS",
                       self._stringify(
                           image.get_metadata_value("Background Exposure (Seconds)")))

        # ========================================================
        elif "luminescent" in image.section:
            ds.add_new((0x0011, 0x1012), "DS",
                       self._stringify(
                           image.get_metadata_value("Luminescent Exposure (Seconds)")))

            ds.add_new((0x0011, 0x1013), "LO",
                       self._stringify(
                           image.get_metadata_value("Luminescent Exposure Units")))

            ds.add_new((0x0011, 0x1002), "US", int(
                self._stringify(
                    image.get_metadata_value("f Number")))
                       )

            ds.add_new((0x0011, 0x1003), "DS",
                       self._stringify(
                           image.get_metadata_value("Field of View")))

            ds.add_new((0x0011, 0x1007), "DS",
                       self._stringify(
                           image.get_metadata_value("Read Bias Level")))

            ds.add_new((0x0011, 0x1005), "LO",
                       self._stringify(
                           image.get_metadata_value("Emission filter")))

            ds.add_new((0x0011, 0x1004), "US", int(
                self._stringify(
                    image.get_metadata_value("Filter Position")))
                       )

            ds.add_new((0x0011, 0x1014), "LO",
                       self._stringify(
                           image.get_metadata_value("Excitation filter")))

            ds.add_new((0x0011, 0x1008), "DS",
                       self._stringify(
                           image.get_metadata_value("Demand Temperature")))

            ds.add_new((0x0011, 0x1009), "DS",
                       self._stringify(
                           image.get_metadata_value("Measured Temperature")))

        return ds

    def _write_dicom(self, out_path, ds):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.save_as(out_path, write_like_original=False)
        print(f"[OK] Saved: {out_path}")

    def _stringify(self, value: str) -> str | None:
        if value is None:
            return ""
        text = str(value).strip()
        return text if text else ""

    def _set_acquisition_datetime(self, ds, image):
        raw_date = image.get_metadata_value("Acquisition Date")
        raw_time = image.get_metadata_value("Acquisition Time")

        if not raw_date or not raw_time:
            now = datetime.now()
            ds.AcquisitionDate = now.strftime("%Y%m%d")
            ds.AcquisitionTime = now.strftime("%H%M%S")
            return

        date_str = str(raw_date).strip()
        time_str = str(raw_time).strip()

        try:
            dt = datetime.strptime(
                f"{date_str} {time_str}",
                "%A, %B %d, %Y %H:%M:%S"
            )
            ds.AcquisitionDate = dt.strftime("%Y%m%d")
            ds.AcquisitionTime = dt.strftime("%H%M%S")
        except ValueError:
            # fallback se il formato cambia
            now = datetime.now()
            ds.AcquisitionDate = now.strftime("%Y%m%d")
            ds.AcquisitionTime = now.strftime("%H%M%S")