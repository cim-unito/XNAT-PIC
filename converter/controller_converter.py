from pathlib import Path
from contextlib import contextmanager

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
        self._model.conversion_type = conversion_type
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
        with self._conversion_progress_dialog():
            self._run_conversion()

    def _run_conversion(self):
        """Run the conversion by preparing, executing, and finalizing steps."""
        try:
            self._prepare_conversion()
            failed_scans = self._perform_conversion()
            self._finalize_conversion()
            self._notify_conversion_outcome(failed_scans)
        except (ValueError, FileNotFoundError, NotADirectoryError,
                PermissionError, RuntimeError) as e:
            self._view.create_alert(str(e))
            self._view.update_page()
        except Exception as e:
            self._view.create_alert(
                f"Error during conversion: {e}"
            )
            self._view.update_page()
            raise

    def _prepare_conversion(self):
        """Prepare the model for conversion and load scans."""
        if self._model.conversion_type is None:
            raise ValueError("Please select a conversion type.")
        if self._model.input_root is None:
            raise ValueError("Please select an input folder before converting.")
        if self._model.level is None:
            raise ValueError("Please select a conversion level.")
        overwrite = self._view.sw_overwrite.value
        self._model.output_root = self._model.input_root
        self._model.create_dicom_output_folder(overwrite)
        self._model.get_input_scans()
        if not self._model.input_scans:
            raise ValueError(
                "No valid scans found for the selected conversion. "
                f"Type: '{self._model.conversion_type.value}', "
                f"level: '{self._model.level.value}', "
                f"input folder: '{self._model.input_root}'."
            )
        self._model.get_output_scans()

    def _perform_conversion(self):
        """Execute conversion for all scans and return failures."""
        failed_scans = []
        total_scans = len(self._model.input_scans)

        for idx, (src, dst) in enumerate(
                zip(self._model.input_scans, self._model.output_scans)
        ):
            try:
                self._model.dicom_converter([str(src), str(dst)])
            except (ValueError, FileNotFoundError, PermissionError,
                    RuntimeError, OSError) as exc:
                failed_scans.append((idx + 1, src, exc))
            finally:
                self._view.update_progress_bar((idx + 1) / total_scans)

        return failed_scans

    def _finalize_conversion(self):
        """Update the UI after the conversion completes."""
        self._treeview_controller.populate_tree(self._model.output_root,
                                                TreeType.DICOM)
        self._view.update_page()

    def _set_level(self, level):
        """Set the conversion level and update the view mode."""
        self._model.level = level
        self._view.set_mode()

    def _notify_conversion_outcome(self, failed_scans):
        """Notify the user about conversion result after finalization."""
        if not failed_scans:
            return

        first_idx, first_src, first_exc = failed_scans[0]
        successful_conversions = len(self._model.input_scans) - len(failed_scans)
        self._view.create_alert(
            f"Conversion completed with partial failures: "
            f"{successful_conversions} succeeded, {len(failed_scans)} failed. "
            f"First failure at scan #{first_idx} ({first_src}): {first_exc}"
        )
        self._view.update_page()

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

    @contextmanager
    def _conversion_progress_dialog(self):
        self._view.show_progress_bar_dialog()
        try:
            yield
        finally:
            self._view.close_progress_bar_dialog()