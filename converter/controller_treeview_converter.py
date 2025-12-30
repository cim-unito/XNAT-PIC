from shared_ui.ui.treeview.controller_treeview import ControllerTreeview


class ControllerTreeviewConverter(ControllerTreeview):
    def __init__(self, model, view, converter_controller):
        super().__init__(model, view)
        self._converter = converter_controller

    def _on_collapse(self, node_path, tile):
        self._converter.folder_path_selected = None
        self._converter.file_path_selected = None

    def _on_expand_selected(self, node_path, tile):
        self._converter.folder_path_selected = node_path
        self._converter.file_path_selected = None

    def _on_file_selected(self, file_path):
        self._converter.file_path_selected = file_path
        self._converter.folder_path_selected = None
        self._converter.on_file_selected(file_path)