import re
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict

@dataclass
class IVISSection:
    name: str
    metadata: dict[str, str] = field(default_factory=dict)
    raw_lines: list[str] = field(default_factory=list)


@dataclass
class IVISImageInfo:
    section: str
    filename: str
    file_path: Path
    metadata: Dict[str, str] = field(default_factory=dict)
    raw_lines: list[str] = field(default_factory=list)


@dataclass
class IVISMetadata:
    sections: list[IVISSection] = field(default_factory=list)
    images: list[IVISImageInfo] = field(default_factory=list)


class IvisMetadataParser:
    SECTION_PATTERN = re.compile(r"^\*\*\*\s*([^:]+):\s*(.*)$")
    KEY_VALUE_PATTERN = re.compile(r"^([^:#\t][^:#]*?):\s*(.*)$")

    IMAGE_KEYWORDS = {
        "photographic image",
        "luminescent image",
        "fluorescent image",
        "readbiasonly image",
    }

    def __init__(self, metadata_file: Path):
        self.metadata_file = metadata_file
        self.section_counter = defaultdict(int)

    def parse(self):
        metadata = IVISMetadata()

        current_section = None
        current_image = None

        with open(self.metadata_file, "r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                stripped = line.strip()

                # ------------------------------------------------------------
                # Blank / comment
                # ------------------------------------------------------------
                if not stripped or stripped.startswith("#"):
                    if current_section:
                        current_section.raw_lines.append(line)
                    if current_image:
                        current_image.raw_lines.append(line)
                    continue

                sec = self.SECTION_PATTERN.match(stripped)
                if sec:
                    base_name = sec.group(1).strip()
                    possible_value = sec.group(2).strip() or None

                    current_section = None
                    current_image = None

                    # ---- IMAGE SECTION ----
                    if base_name.lower() in self.IMAGE_KEYWORDS:
                        filename = (
                            possible_value
                            if possible_value
                               and possible_value.lower().endswith(
                                (".tif", ".tiff"))
                            else None
                        )
                        if filename:
                            file_path = self.metadata_file.parent / filename
                            current_image = IVISImageInfo(
                                section=base_name, filename=filename,
                                file_path=file_path
                            )
                        current_image.raw_lines.append(line)
                        metadata.images.append(current_image)
                        continue

                    # ---- NORMAL SECTION ----
                    count = self.section_counter[base_name]
                    name = base_name if count == 0 else f"{base_name} ({count})"
                    self.section_counter[base_name] += 1

                    current_section = IVISSection(name=name)
                    current_section.raw_lines.append(line)
                    metadata.sections.append(current_section)

                    if possible_value:
                        self._store(
                            current_section.metadata,
                            base_name,
                            possible_value,
                        )
                    continue

                # ------------------------------------------------------------
                # KEY : VALUE
                # ------------------------------------------------------------
                kv = self.KEY_VALUE_PATTERN.match(stripped)
                if kv:
                    key = kv.group(1).strip()
                    value_raw = kv.group(2)
                    value_clean = value_raw.split("#", 1)[0].strip()
                    value = value_clean

                    if current_image:
                        if (
                                current_image.filename is None
                                and isinstance(value, str)
                                and value.lower().endswith((".tif", ".tiff"))
                        ):
                            current_image.filename = value
                        else:
                            self._store(current_image.metadata, key, value)

                        current_image.raw_lines.append(line)
                        continue

                    if current_section:
                        self._store(current_section.metadata, key, value)
                        current_section.raw_lines.append(line)
                        continue

                # ------------------------------------------------------------
                # UNPARSED LINE
                # ------------------------------------------------------------
                if current_section:
                    current_section.raw_lines.append(line)
                if current_image:
                    current_image.raw_lines.append(line)

        return metadata

    @staticmethod
    def _store(target: dict, key: str, value: Any):
        if key not in target:
            target[key] = value
            return

        existing = target[key]

        if isinstance(existing, list):
            if value != existing[-1]:
                existing.append(value)
        else:
            if value != existing:
                target[key] = [existing, value]