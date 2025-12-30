import flet as ft


class ControllerMainInterface:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds
        # the data
        self._model = model

    def go_to_converter(self):
        self._view.page.go("/converter")

    def go_to_uploader(self):
        self._view.page.go("/uploader")

    def go_to_custom_form(self):
        self._view.page.go("/custom_form")
