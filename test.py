import flet as ft
import json


def main(page: ft.Page):

    def edit_json(e):

        # JSON iniziale
        data = {
            "form": {"uuid": "c1b8c1e0-4d85-4b55-9b92-33a7f98eac12",
                     "name": "Dose Assessment Form",
                     "description": "Form personalizzato per registrare dati di dose in un progetto XNAT",
                     "scope": "project",
                     "projectId": "MYPROJECT1",
                     "fields": [
                         {"name": "dose_text", "label": "Dose (testo)", "datatype": "string"},
                         {"name": "dose_value", "label": "Dose (valore numerico)", "datatype": "float"},
                         {"name": "dose_unit", "label": "Unità dose", "datatype": "string"},
                         {"name": "dose_type", "label": "Tipo di dose", "datatype": "string"},
                         {"name": "notes", "label": "Note aggiuntive", "datatype": "string"},
                         {"name": "acquisition_date", "label": "Data acquisizione", "datatype": "date"},
                     ]}
        }

        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)

        # EDITOR JSON
        editor = ft.TextField(
            value=formatted_json,
            multiline=True,
            expand=True,
            min_lines=25,
            max_lines=None,
            text_style=ft.TextStyle(font_family="Courier New", size=14),
            border=ft.InputBorder.OUTLINE
        )

        # FUNZIONI ---------------------

        def format_json(_):
            try:
                j = json.loads(editor.value)
                editor.value = json.dumps(j, indent=4, ensure_ascii=False)
                page.update()
            except Exception as ex:
                show_error(ex)

        def save_json(_):
            try:
                json.loads(editor.value)
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(ex)

        def show_error(ex):
            page.snack_bar = ft.SnackBar(ft.Text(f"Errore JSON: {ex}"), bgcolor=ft.colors.RED_400)
            page.snack_bar.open = True
            page.update()

        # SCROLL UNIVERSALE: Column(scroll=True)
        scroll_area = ft.Column(
            controls=[editor],
            scroll=True,
            expand=True,
            width=900,
            height=550,
        )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editor JSON"),
            content=scroll_area,
            actions=[
                ft.TextButton("Formatta", on_click=format_json),
                ft.TextButton("Salva", on_click=save_json),
                ft.TextButton("Chiudi", on_click=lambda _: setattr(dlg, "open", False)),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.open(dlg)
        page.update()

    page.add(ft.ElevatedButton("Apri Editor JSON", on_click=edit_json))


ft.app(target=main)
