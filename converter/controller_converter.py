from pathlib import Path

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
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._treeview_model = ModelTreeview()
        self._treeview_view = ViewTreeview(self._view)
        self._treeview_controller = ControllerTreeview(
            self._treeview_model,
            self._treeview_view,
            self
        )

    # -------------------------------------------------------
    # HOME / BACK
    # -------------------------------------------------------
    def go_home(self):
        self._view.page.go("/")

    def on_home_back_clicked(self, e):
        if self._model.level is None:
            self._view.set_initial_state()
            self.go_home()
        else:
            self._model.reset_level()
            self._view.set_initial_state()

    # -------------------------------------------------------
    # SET MODE
    # -------------------------------------------------------
    def _set_mode_for_level(self):
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
        self._set_mode_for_level()

    def convert_project(self, e):
        self.set_level(ConverterLevel.PROJECT)

    def convert_subject(self, e):
        self.set_level(ConverterLevel.SUBJECT)

    def convert_experiment(self, e):
        self.set_level(ConverterLevel.EXPERIMENT)

    def conversion_type(self, e):
        self._model.conversion_type = ConverterType(e.control.value)
        print(e.control.value)

    # -------------------------------------------------------
    # TREEVIEW RAW DATA/DICOM FILES
    # -------------------------------------------------------
    def get_directory_to_convert(self, path: str):
        self._model.input_root = path
        self._treeview_controller.populate_tree(Path(path), TreeType.RAW)

    def on_file_selected(self, e, file_path):
        """File selected"""
        self._view.set_selected_control(e.control)
        print(f"[SELECTED FILE] {file_path}")
        self._view.update_page()

    def _on_treeview_collapse(self, node_path, tile):
        self.folder_path_selected = None
        self.file_path_selected = None

    def _on_treeview_expand(self, node_path, tile):
        self.folder_path_selected = node_path
        self.file_path_selected = None

    def _on_treeview_file_selected(self, file_path):
        self.file_path_selected = file_path
        self.folder_path_selected = None

    # -------------------------------------------------------
    # DICOM CONVERTER
    # -------------------------------------------------------
    def on_convert_clicked(self, e):
        self._view.show_progress_dialog()
        # threading.Thread(target=self.run_conversion, daemon=True).start()
        self._run_conversion()

    def _run_conversion(self):
        try:
            self._prepare_conversion()
            self._perform_conversion()
            self._finalize_conversion()
        except Exception as e:
            print(str(e))

    def _prepare_conversion(self):
        overwrite = self._view.sw_overwrite.value
        self._model.output_root = self._model.input_root
        self._model.create_dicom_output_folder(overwrite)
        self._model.get_input_scans()
        self._model.get_output_scans()

    def _perform_conversion(self):
        total_scans = len(self._model.input_scans)

        for idx, (src, dst) in enumerate(
                zip(self._model.input_scans, self._model.output_scans)
        ):
            self._model.dicom_converter([str(src), str(dst)])

            self._view.update_progress((idx + 1) / total_scans)

    def _finalize_conversion(self):
        self.populate_tree(self._model.output_root, TreeType.DICOM)
        self._view.dlg_conversion.open = False
        self._view.update_page()
