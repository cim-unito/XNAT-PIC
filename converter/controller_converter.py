import threading

import flet as ft
from pathlib import Path

from converter.bruker_2_dicom_converter import Bruker2DicomConverter
from enums.converter_level import ConverterLevel
from enums.tree_type import TreeType


class ControllerConverter:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

        self._mode_selected = None

    # -------------------------------------------------------
    # HOME / BACK
    # -------------------------------------------------------
    def go_home(self):
        self._view._page.go("/")

    def on_home_back_clicked(self, e):
        self._view.set_initial_state()
        if self._mode_selected is None:
            self.go_home()
        else:
            self._mode_selected = None

    # -------------------------------------------------------
    # SET MODE
    # -------------------------------------------------------
    def _set_mode_for_level(self, mode):
        self._mode_selected = mode

        self._view.set_mode(
            top_level_buttons_enabled=False,
            sw_enabled=True,
            select_folder_enabled=True,
            convert_enabled=True,
        )

    # -------------------------------------------------------
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT)
    # -------------------------------------------------------
    def set_level(self, level):
        self._model.level = level
        self._set_mode_for_level(level.value)

    def convert_project(self, e):
        self.set_level(ConverterLevel.project)
        print(self._view.dd_conversion_type.value)

    def convert_subject(self, e):
        self.set_level(ConverterLevel.subject)

    def convert_experiment(self, e):
        self.set_level(ConverterLevel.experiment)

    def conversion_type(self, e):
        # print(e.control.value)
        pass

    # -------------------------------------------------------
    # TREEVIEW RAW DATA/DICOM FILES
    # -------------------------------------------------------
    def get_directory_to_convert(self, path: str):
        self._model.path_to_convert = path
        self.populate_tree(Path(path), TreeType.RAW)

    def populate_tree(self, path: Path, tree_type: TreeType):
        """Initial tree loading"""
        try:
            items = self._model.get_list_directory(path)
        except Exception as err:
            self._view.create_alert(str(err))
            return

        widget = self._view.build_lazy_tree(
            items,
            expand_callback=self.on_expand,
            file_selected_callback=self.on_file_selected
        )

        self._view.update_tree(widget, tree_type)

    def on_expand(self, e, node_path: Path, tile):
        """Folder expansion"""
        if e.data != "true":  # collapse → ignora
            return

        try:
            children = self._model.get_list_directory(node_path)
        except Exception as err:
            self._view.create_alert(str(err))
            return

        self._view.update_expansion_tile(
            tile,
            children,
            expand_callback=self.on_expand,
            file_selected_callback=self.on_file_selected
        )

        # salvataggio selezione data
        self._model.selected_path = node_path

        # highlight nel tree
        self._view.set_selected_control(tile)

        # stampa della selezione
        print(f"[SELECTED DIR] {node_path}")

        self._view.update_page()

    def on_file_selected(self, e, file_path: str):
        """File selected"""
        self._model.selected_path = file_path
        self._view.set_selected_control(e.control)
        print(f"[SELECTED FILE] {file_path}")
        self._view.update_page()

    # -------------------------------------------------------
    # DICOM CONVERTER
    # -------------------------------------------------------
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
            if self._model.conversion_type == "Bruker2DICOM":
                Bruker2DicomConverter.convert(self._model, [str(src), str(dst)])
            elif self._model.conversion_type == "IVIS2DICOM":
                self._model.ivis2dicom_converter([str(src), str(dst)])

            self._view.update_progress((idx + 1) / total_scans)

        self.populate_tree(self._model.path_converted, type_tree='dcm')
        self._view.dlg_conversion.open = False
        self._view.update_page()
