from pathlib import Path
from typing import List, Dict

class FilesystemService:

    @staticmethod
    def get_list_directory(path: Path) -> List[Dict]:
        """
        Returns a list of dict with name, path, is_dir.
        """
        try:
            # Sorting criterion:
            # - All directories before files
            # - Within groups (directories and files), case-insensitive
            # alphabetical sorting
            children = sorted(
                path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            return [{
                "name": "[access denied]",
                "path": path,
                "is_dir": False
            }]
        except FileNotFoundError:
            raise ValueError(f"Path not found: {path}")

        items = []
        for child in children:
            if child.name.startswith("."):
                continue

            items.append({
                "name": child.name,
                "path": child,
                "is_dir": child.is_dir(),
            })

        return items

