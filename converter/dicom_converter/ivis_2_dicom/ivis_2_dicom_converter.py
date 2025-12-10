import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from converter.dicom_converter.ivis_2_dicom.ivis_metadata_parser import \
    IvisMetadataParser


# class IvisImageLocator:
#
#     def locate(self, src: Path, metadata: IVISMetadata) -> Dict[str, Path]:
#         files = {f.name.lower(): f for f in src.iterdir() if f.is_file()}
#         found = {}
#
#         for img in metadata.images:
#             if not img.filename:
#                 continue
#
#             fname = img.filename.lower()
#
#             if fname not in files:
#                 raise FileNotFoundError(
#                     f"Immagine '{img.filename}' dichiarata nel metadata ma non trovata in {src}"
#                 )
#
#             found[img.filename] = files[fname]
#
#         return found


class Ivis2DicomConverter:
    def __init__(self):
        self._src = None
        self._dst = None

    def convert(self, src_dst):
        self._src = Path(src_dst[0])
        self._dst = Path(src_dst[1])

        metadata_file = self._find_metadata_file()
        if not metadata_file:
            print("ClickInfo metadata file not found")

        metadata = IvisMetadataParser(metadata_file).parse()
        # images = IvisImageLocator().locate(self._src, metadata)

        # study = IvisStudy(
        #     src_path=self._src,
        #     dst_path=self._dst,
        #     metadata=metadata,
        #     images=images
        # )

        # Qui in futuro aggiungerai:
        # self._generate_dicom(study)

        return study

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

