from pathlib import Path
from typing import List, Dict

from shared_ui.services.filesystem_service import FilesystemService


class ModelTreeview:
    @staticmethod
    def get_list_directory_treeview(path: Path) -> List[Dict]:
        return FilesystemService.get_list_directory_treeview(path)