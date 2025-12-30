from pathlib import Path

from shared_ui.services.filesystem_service import FilesystemService


class ModelTreeview:
    def get_list_directory_treeview(self, path: Path):
        return FilesystemService.get_list_directory_treeview(path)