import threading

import flet as ft
from pathlib import Path

from converter.bruker_2_dicom_converter import Bruker2DicomConverter

class ControllerConverter:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def go_home(self):
        self._view._page.go("/")

    def toggle_folder_selection(self, e):
        for btn in (self._view.btn_project, self._view.btn_subject,
                    self._view.btn_experiment):
            btn.disabled = not btn.disabled
        self._view.btn_select_folder.disabled = not self._view.btn_select_folder.disabled
        self._view.update_page()

    def convert_project(self, e):
        self.toggle_folder_selection(e)
        self._model.level = "project"

    def convert_subject(self, e):
        self.toggle_folder_selection(e)
        self._model.level = "subject"

    def convert_experiment(self, e):
        self.toggle_folder_selection(e)
        self._model.level = "experiment"

    def get_directory_to_convert(self, path):
        self._model.path_to_convert = path
        self.populate_tree(Path(path))

    def populate_tree(self, path, type_tree='src'):
        try:
            root_items = self._model.list_directory(path)
            tree_widget = self._view.build_lazy_tree(root_items,
                                                     self.on_expand,
                                                     self.on_file_selected)
            self._view.update_tree(tree_widget, type_tree)
        except ValueError as err:
            self._view.create_alert(str(err))

    def on_expand(self, e, node_path: str, expansion_tile):
        children = self._model.list_directory(node_path)
        expansion_tile.controls.clear()
        for child in children:
            if child["is_dir"]:
                sub_tile = self._view.make_lazy_folder(child, self.on_expand)
                expansion_tile.controls.append(sub_tile)
            else:
                file_tile = self._view.make_file_tile(child,
                                                      self.on_file_selected)
                expansion_tile.controls.append(file_tile)
        self._view.update_page()

    def on_file_selected(self, file_path: str):
        print(f"File selected: {file_path}")

    def dicom_converter(self, e):
        self._view.show_progress_dialog()
        # threading.Thread(target=self.run_conversion, daemon=True).start()
        self.run_conversion()

    def run_conversion(self):
        flag_overwrite = self._view.sw_existing_folder.value
        p = self._model.path_to_convert
        self._model.path_converted = p.parent / (p.name + "_dcm")
        self._model.create_dicom_folder(flag_overwrite)
        self._model.get_valid_scans()
        self._model.get_destination_scans()

        total_scans = len(self._model.scan_to_convert)

        for idx, (src, dst) in enumerate(
                zip(self._model.scan_to_convert, self._model.scan_converted)
        ):
            Bruker2DicomConverter.convert(self._model, [str(src), str(dst)])
            self._view.update_progress((idx + 1) / total_scans)

        self.populate_tree(self._model.path_converted, type_tree='dcm')
        self._view.dlg_conversion.open = False
        self._view.update_page()
