from pathlib import Path

from enums.tree_type import TreeType
from shared_ui.services.filesystem_service import FilesystemService


class ControllerTreeview:
    def populate_tree(self, path: Path, tree_type: TreeType):
        """Initial tree loading"""
        try:
            items = FilesystemService().get_list_directory_treeview(path)
        except Exception as err:
            return

        widget = self._view.build_lazy_tree(
            items,
            expand_callback=self.on_expand,
            file_selected_callback=self.on_file_selected
        )

        self._view.update_tree(widget, tree_type)

    def on_expand(self, e, node_path, tile):
        """Folder expansion"""
        if e.data != "true":
            self._on_collapse(node_path, tile)
            return

        try:
            children = self._model.get_list_directory_treeview(node_path)
        except Exception as err:
            self._view.create_alert(str(err))
            return

        self._view.update_expansion_tile(
            tile,
            children,
            expand_callback=self.on_expand,
            file_selected_callback=self.on_file_selected
        )

        self._view.set_selected_control(tile)
        self._on_expand_selected(node_path, tile)
        self._view.update_page()

    def on_file_selected(self, e, file_path):
        """File selected"""
        self._view.set_selected_control(e.control)
        self._on_file_selected(file_path)
        self._view.update_page()

    def _on_collapse(self, node_path, tile):
        return

    def _on_expand_selected(self, node_path, tile):
        return

    def _on_file_selected(self, file_path):
        return