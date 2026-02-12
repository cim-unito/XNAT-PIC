from pathlib import Path

import flet as ft

from enums.converter_level import ConverterLevel
from enums.converter_type import ConverterType
from enums.tree_type import TreeType
from shared_ui.ui.treeview.controller_treeview import ControllerTreeview
from shared_ui.ui.treeview.model_treeview import ModelTreeview
from shared_ui.ui.treeview.view_treeview import ViewTreeview


class ControllerConverter:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the
        # data
        self._model = model
        # treeview
        self._treeview_model = ModelTreeview()
        self._treeview_view = ViewTreeview(self._view)
        self._treeview_controller = ControllerTreeview(
            self._treeview_model,
            self._treeview_view,
            on_collapse=self._on_treeview_collapse,
            on_expand_selected=self._on_treeview_expand,
            on_file_selected=self._on_treeview_file_selected,
        )

    # -------------------------------------------------------
    # HOME / BACK
    # -------------------------------------------------------
    def go_home(self):
        """Navigate the application back to the home page."""
        self._view.page.go("/")

    def on_home_back_clicked(self, e: ft.ControlEvent):
        """Handle the home/back click by restoring the initial UI state."""
        if self._model.level is None:
            self._model.reset_level()
            self._view.set_initial_state()
            self.go_home()
        else:
            self._model.reset_level()
            self._view.set_initial_state()

    # -------------------------------------------------------
    # SET LEVEL (PROJECT / SUBJECT / EXPERIMENT)
    # -------------------------------------------------------
    def convert_project(self, e: ft.ControlEvent):
        """Start a project-level conversion and open the directory picker."""
        self._set_level(ConverterLevel.PROJECT)
        self._view.open_directory_picker()

    def convert_subject(self, e: ft.ControlEvent):
        """Start a subject-level conversion and open the directory picker."""
        self._set_level(ConverterLevel.SUBJECT)
        self._view.open_directory_picker()

    def convert_experiment(self, e: ft.ControlEvent):
        """Start an experiment-level conversion and open the directory picker."""
        self._set_level(ConverterLevel.EXPERIMENT)
        self._view.open_directory_picker()

    def set_conversion_type(self, conversion_type: ConverterType):
        """Update the conversion type selected by the user."""
        self._view.txt_conversion_type.value = conversion_type.value
        self._view.update_page()

    # -------------------------------------------------------
    # TREEVIEW RAW DATA/DICOM FILES
    # -------------------------------------------------------
    def get_directory_to_convert(self, path: str):
        """Set the input directory and populate the treeview with RAW data."""
        self._model.input_root = path
        self._treeview_controller.populate_tree(Path(path), TreeType.RAW)

    # -------------------------------------------------------
    # DICOM CONVERTER
    # -------------------------------------------------------
    def on_convert_clicked(self, e):
        """Start the conversion and show the progress dialog."""
        self._view.show_progress_bar_dialog()
        # threading.Thread(target=self.run_conversion, daemon=True).start()
        self._run_conversion()

    def _run_conversion(self):
        """Run the conversion by preparing, executing, and finalizing steps."""
        try:
            self._prepare_conversion()
            self._perform_conversion()
            self._finalize_conversion()
        except Exception as e:
            self._view.dlg_conversion.open = False
            self._view.create_alert(str(e))
            self._view.update_page()

    def _prepare_conversion(self):
        """Prepare the model for conversion and load scans."""
        if self._model.conversion_type is None:
            raise ValueError("Please select a conversion type.")
        overwrite = self._view.sw_overwrite.value
        self._model.output_root = self._model.input_root
        self._model.create_dicom_output_folder(overwrite)
        self._model.get_input_scans()
        self._model.get_output_scans()

    def _perform_conversion(self):
        """Execute the DICOM conversion while updating progress."""
        total_scans = len(self._model.input_scans)

        for idx, (src, dst) in enumerate(
                zip(self._model.input_scans, self._model.output_scans)
        ):
            self._model.dicom_converter([str(src), str(dst)])

    def _finalize_conversion(self):
        """Update the UI after the conversion completes."""
        self._treeview_controller.populate_tree(self._model.output_root,
                                                TreeType.DICOM)
        self._view.dlg_conversion.open = False
        self._view.update_page()

    def _set_level(self, level):
        """Set the conversion level and update the view mode."""
        self._model.level = level
        self._view.set_mode()

    def _on_treeview_collapse(self, node_path, tile):
        """Handle a treeview node collapse."""
        self.folder_path_selected = None
        self.file_path_selected = None

    def _on_treeview_expand(self, node_path, tile):
        """Handle a treeview node expansion."""
        self.folder_path_selected = node_path
        self.file_path_selected = None

    def _on_treeview_file_selected(self, file_path):
        """Handle a file selection in the treeview."""
        self.file_path_selected = file_path
        self.folder_path_selected = None