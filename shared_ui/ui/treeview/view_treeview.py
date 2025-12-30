from pathlib import Path
from typing import List, Dict, Callable

import flet as ft

from enums.tree_type import TreeType


class ViewTreeview:
    def __init__(self, host_view=None):
        self._host_view = host_view
        self._selected_control = None

    def build_lazy_tree(
            self,
            items: List[Dict],
            expand_callback: Callable[
                [ft.ControlEvent, Path, ft.Control], None],
            file_selected_callback: Callable[[ft.ControlEvent, Path], None],
    ) -> ft.ListView:
        """Build the lazy-loading tree list view for the provided items."""
        tiles = [
            self._build_node(item, expand_callback, file_selected_callback)
            for item in items
        ]
        return ft.ListView(controls=tiles, expand=True)

    def update_tree(self, new_widget: ft.ListView, tree_type: TreeType):
        if self._host_view:
            self._host_view.update_tree(new_widget, tree_type)

    def create_alert(self, message: str):
        if self._host_view:
            self._host_view.create_alert(message)

    def update_page(self):
        if self._host_view:
            self._host_view.update_page()

    def update_expansion_tile(self,
                              tile: ft.ExpansionTile,
                              children: list[Dict],
                              expand_callback: Callable[
                                  [ft.ControlEvent, Path, ft.Control], None],
                              file_selected_callback: Callable[
                                  [ft.ControlEvent, Path], None]):
        """Replace the children of the expansion tile with new nodes."""
        tile.controls.clear()

        if not children:
            tile.controls.append(ft.Text("Empty folder"))
        else:
            for item in children:
                node = self._build_node(item, expand_callback,
                                        file_selected_callback)
                tile.controls.append(node)

    def set_selected_control(self, control: ft.Control):
        if self._selected_control:
            self._clear_selection(self._selected_control)

        self._apply_selection(control)
        self._selected_control = control

    def get_selected_control(self):
        return self._selected_control

    def _build_node(self,
                    item: Dict,
                    expand_callback: Callable[
                        [ft.ControlEvent, Path, ft.Control], None],
                    file_selected_callback: Callable[
                        [ft.ControlEvent, Path], None]
                    ):
        if item["is_dir"]:
            return self._make_lazy_folder(item, expand_callback)
        return self._make_file_tile(item, file_selected_callback)

    @staticmethod
    def _make_lazy_folder(
            item: Dict,
            expand_callback: Callable[
                [ft.ControlEvent, Path, ft.Control], None],
    ) -> ft.ExpansionTile:
        return ft.ExpansionTile(
            leading=ft.Icon(ft.Icons.FOLDER),
            title=ft.Text(item["name"]),
            controls=[ft.Text("Loading...")],
            on_change=lambda e, path=item["path"]: expand_callback(
                e, path, e.control
            ),
            data=item["path"],
        )

    @staticmethod
    def _make_file_tile(
            item: Dict,
            file_selected_callback: Callable[[ft.ControlEvent, Path], None],
    ) -> ft.ListTile:
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.DESCRIPTION),
            title=ft.Text(item["name"]),
            on_click=lambda e, path=item["path"]: file_selected_callback(
                e, path
            )
        )

    @staticmethod
    def _apply_selection(control: ft.Control):
        control.bgcolor = ft.Colors.AMBER_100

    @staticmethod
    def _clear_selection(control: ft.Control):
        control.bgcolor = None
