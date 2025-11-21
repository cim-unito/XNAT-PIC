import flet as ft


class ViewXnatNewProject(ft.Control):
    """
    Dialog minimale per creare un nuovo progetto XNAT.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._controller = None

        self.dlg: ft.AlertDialog | None = None

        # controls
        self.txt_title: ft.TextField | None = None
        self.txt_project_id: ft.TextField | None = None
        self.chk_edit_id: ft.Checkbox | None = None

        self.rb_access: ft.RadioGroup | None = None
        self.txt_description: ft.TextField | None = None

        self.txt_keyword: ft.TextField | None = None
        self.keyword_chips_row: ft.Row | None = None

        self.dd_investigator: ft.Dropdown | None = None

        self.btn_submit: ft.ElevatedButton | None = None

    # --------------------------------------------------
    # BIND CONTROLLER
    # --------------------------------------------------
    def set_controller(self, controller):
        self._controller = controller

    # --------------------------------------------------
    # COSTRUZIONE DIALOG
    # --------------------------------------------------
    def build_dialog(self, on_created, on_cancel=None) -> ft.AlertDialog:
        # collega callback al controller
        self._controller.set_callbacks(on_created, on_cancel)

        # titolo
        self.txt_title = ft.TextField(
            label="Project title *",
            on_change=lambda e: self._controller.on_title_changed(e.control.value),
        )

        # project ID
        self.txt_project_id = ft.TextField(
            label="Project ID *",
            disabled=True,
            on_change=lambda e: self._controller.on_project_id_changed(e.control.value),
        )
        self.chk_edit_id = ft.Checkbox(
            label="Edit ID",
            value=False,
            on_change=lambda e: self._controller.on_toggle_edit_id(e.control.value),
        )

        id_row = ft.Row(
            controls=[self.txt_project_id, self.chk_edit_id],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # access radio
        self.rb_access = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value="private", label="Private"),
                    ft.Radio(value="protected", label="Protected"),
                    ft.Radio(value="public", label="Public"),
                ],
                spacing=10,
            ),
            value="private",
            on_change=lambda e: self._controller.on_access_changed(e.control.value),
        )

        # descrizione
        self.txt_description = ft.TextField(
            label="Project description",
            multiline=True,
            min_lines=3,
            max_lines=6,
            on_change=lambda e: self._controller.on_description_changed(
                e.control.value
            ),
        )

        # keywords
        self.txt_keyword = ft.TextField(
            label="Add keyword (press Enter)",
            on_submit=lambda e: self._on_keyword_submit(e),
        )
        self.keyword_chips_row = ft.Row(spacing=5, wrap=True)

        # investigators dropdown
        self.dd_investigator = ft.Dropdown(
            label="Investigator",
            options=[],
            on_change=lambda e: self._controller.on_investigator_selected(
                e.control.value
            ),
            hint_text="-- none --",
        )
        btn_new_inv = ft.TextButton(
            "New investigator...",
            on_click=lambda e: self._open_new_investigator_dialog(),
        )

        investigators_row = ft.Row(
            controls=[self.dd_investigator, btn_new_inv],
            spacing=10,
        )

        # bottoni bottom
        btn_cancel = ft.TextButton("Close", on_click=self._controller.cancel)
        self.btn_submit = ft.ElevatedButton(
            "Submit",
            disabled=True,
            on_click=self._controller.submit,
        )

        # contenuto dialog
        content = ft.Column(
            width=600,
            tight=False,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                self.txt_title,
                id_row,
                ft.Text("Accessibility"),
                self.rb_access,
                self.txt_description,
                ft.Text("Keywords"),
                self.txt_keyword,
                self.keyword_chips_row,
                ft.Text("Investigators"),
                investigators_row,
            ],
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("New XNAT Project"),
            content=content,
            actions=[btn_cancel, self.btn_submit],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # carica investigators
        self._controller.load_investigators()

        return self.dlg

    # --------------------------------------------------
    # SUPPORTO KEYWORDS
    # --------------------------------------------------
    def _on_keyword_submit(self, e: ft.ControlEvent):
        kw = e.control.value.strip()
        if kw:
            self._controller.on_add_keyword(kw)
        e.control.value = ""
        self._page.update()

    def update_keywords(self, keywords: list[str]):
        chips = []
        for kw in keywords:
            # attenzioe alla lambda: catturiamo kw come default arg
            chips.append(
                ft.Chip(
                    label=ft.Text(kw),
                    on_deleted=lambda e, v=kw: self._controller.on_remove_keyword(v),
                )
            )
        self.keyword_chips_row.controls = chips
        self._page.update()

    # --------------------------------------------------
    # INVESTIGATORS
    # --------------------------------------------------
    def populate_investigators(self, items: list[str]):
        self.dd_investigator.options = [
            ft.dropdown.Option(text=txt, key=txt, value=txt) for txt in items
        ]
        self.dd_investigator.value = None
        self._page.update()

    def _open_new_investigator_dialog(self):
        """
        Dialog minimale per aggiungere un nuovo investigator.
        """
        txt_first = ft.TextField(label="First name")
        txt_last = ft.TextField(label="Last name")
        txt_inst = ft.TextField(label="Institution")
        txt_email = ft.TextField(label="Email")

        def on_add(e):
            fn = txt_first.value.strip()
            ln = txt_last.value.strip()
            if not fn or not ln:
                self.show_error("First name and last name are required.")
                return
            self._controller.create_investigator(
                firstname=fn,
                lastname=ln,
                institution=txt_inst.value.strip(),
                email=txt_email.value.strip(),
            )
            self._page.close(dlg_inv)
            self._page.update()

        dlg_inv = ft.AlertDialog(
            modal=True,
            title=ft.Text("New investigator"),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[txt_first, txt_last, txt_inst, txt_email],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._page.close(dlg_inv)),
                ft.ElevatedButton("Add", on_click=on_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._page.open(dlg_inv)
        self._page.update()

    # --------------------------------------------------
    # API CHIAMATE DAL CONTROLLER
    # --------------------------------------------------
    def set_project_id_value(self, value: str):
        self.txt_project_id.value = value
        self._page.update()

    def set_project_id_editable(self, editable: bool):
        self.txt_project_id.disabled = not editable
        self._page.update()

    def set_submit_enabled(self, enabled: bool):
        self.btn_submit.disabled = not enabled
        self._page.update()

    def close_dialog(self):
        if self.dlg:
            self._page.close(self.dlg)
            self._page.update()

    def show_error(self, msg: str):
        dlg = ft.AlertDialog(title=ft.Text(msg))
        self._page.open(dlg)
        self._page.update()
