import flet as ft


class ViewTreeview:
    def __init__(self, host_view=None):
        self._host_view = host_view
        self._selected_control = None

    def build_lazy_tree(self, items, expand_callback, file_selected_callback):
        tiles = [
            self._build_node(item, expand_callback, file_selected_callback)
            for item in items
        ]
        return ft.ListView(controls=tiles, expand=True)

    def update_tree(self, new_widget: ft.ListView, tree_type):
        if self._host_view:
            self._host_view.update_tree(new_widget, tree_type)

    def create_alert(self, message):
        if self._host_view:
            self._host_view.create_alert(message)

    def update_page(self):
        if self._host_view:
            self._host_view.update_page()

    def update_expansion_tile(self, tile, children, expand_callback,
                              file_selected_callback):
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

    def _build_node(self, item, expand_callback, file_selected_callback):
        if item["is_dir"]:
            return self._make_lazy_folder(item, expand_callback)
        return self._make_file_tile(item, file_selected_callback)

    @staticmethod
    def _make_lazy_folder(item, expand_callback):
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
    def _make_file_tile(item, file_selected_callback):
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
