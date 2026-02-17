import flet as ft

class ViewXnatNewProject:
    def __init__(self, page: ft.Page, on_submit, on_cancel=None):
        self._page = page
        self._controller = None
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        self.dlg = None
        self.txt_title = None
        self.txt_project_id = None
        self.chk_edit_id = None
        self.rb_access = None
        self.txt_description = None
        self.btn_submit = None
        self.btn_cancel = None

        self.build_dialog()

    def build_dialog(self):
        self.txt_title = ft.TextField(label="Project title *")

        self.txt_project_id = ft.TextField(
            label="Project ID *",
            disabled=True,
        )

        self.chk_edit_id = ft.Checkbox(label="Edit ID")

        id_row = ft.Row(
            [self.txt_project_id, self.chk_edit_id],
            spacing=10
        )

        self.rb_access = ft.RadioGroup(
            value="private",
            content=ft.Row(
                controls=[
                    ft.Radio(value="private", label="Private"),
                    ft.Radio(value="protected", label="Protected"),
                    ft.Radio(value="public", label="Public")
                ]
            )
        )

        self.txt_description = ft.TextField(
            label="Project description",
            multiline=True,
            min_lines=1,
            max_lines=6
        )

        self.btn_cancel = ft.TextButton("Close", on_click=self._on_cancel)
        self.btn_submit = ft.ElevatedButton(
            "Submit",
            disabled=True,
            on_click=self._on_submit
        )

        content = ft.Column(
            width=600,
            spacing=10,
            controls=[
                self.txt_title,
                id_row,
                ft.Text("Accessibility"),
                self.rb_access,
                self.txt_description
            ]
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("New XNAT Project"),
            content=content,
            actions=[self.btn_cancel, self.btn_submit]
        )

    def open(self):
        if not self.dlg:
            self.build_dialog()

        self._page.open(self.dlg)
        self._page.update()

    def reset_form(self):
        self.txt_title.value = ""
        self.txt_project_id.value = ""
        self.txt_project_id.disabled = True
        self.chk_edit_id.value = False
        self.rb_access.value = "private"
        self.txt_description.value = ""
        self.btn_submit.disabled = True
        self._page.update()

    def close(self):
        self._page.close(self.dlg)
        self._page.update()

    def set_project_id_value(self, value):
        self.txt_project_id.value = value
        self._page.update()

    def set_submit_enabled(self, enabled):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def set_controller(self, controller):
        self._controller = controller

    def _on_submit(self, e):
        data = {
            "project_name": self.txt_title.value,
            "project_id": self.txt_project_id.value,
            "accessibility": self.rb_access.value,
            "description": self.txt_description.value,
        }

        if self.on_submit_callback:
            self.on_submit_callback(data)

        self.close()

    def _on_cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.close()
