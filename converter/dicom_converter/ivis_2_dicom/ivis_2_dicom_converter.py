from pathlib import Path

from converter.dicom_converter.ivis_2_dicom.ivis_metadata_parser import \
    IvisMetadataParser, IvisMetadata, IvisImageInfo

from converter.dicom_converter.ivis_2_dicom.ivis_dicom_generator import \
    IvisDicomGenerator


class Ivis2DicomConverter:
    def __init__(self):
        self._src = None
        self._dst = None

    def convert(self, src_dst: list[str]) -> tuple[int, list[tuple[Path, Exception]]]:
        self._src = Path(src_dst[0])
        self._dst = Path(src_dst[1])

        path_metadata_file = self._find_metadata_file()
        if not path_metadata_file:
            raise ValueError("ClickInfo metadata file not found.")

        try:
            metadata_parser = IvisMetadataParser(path_metadata_file).parse()
        except Exception as e:
            raise e

        return IvisDicomGenerator(metadata_parser).generate_dicom(self._dst)

    def _find_metadata_file(self) -> Path | None:
        """
        Search for the ClickInfo. If it isn't there, get the file that
        contains the word clickinfo (for example AnalyzedClickInfo).
        """
        files = [f for f in self._src.iterdir() if f.is_file()]

        for f in files:
            if f.stem.lower() == "clickinfo":
                return f

        for f in files:
            if "clickinfo" in f.name.lower():
                return f

        return None
