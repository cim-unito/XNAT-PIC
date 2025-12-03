from main_interface.model_main_interface import ModelMainInterface
from main_interface.view_main_interface import ViewMainInterface
from main_interface.controller_main_interface import ControllerMainInterface

from converter.model_converter import ModelConverter
from converter.view_converter import ViewConverter
from converter.controller_converter import ControllerConverter

from uploader.model_uploader import ModelUploader
from uploader.view_uploader import ViewUploader
from uploader.controller_uploader import ControllerUploader

from custom_form.model_custom_form import ModelCustomForm
from custom_form.view_custom_form import ViewCustomForm
from custom_form.controller_custom_form import ControllerCustomForm

from xnat_auth.model_xnat_auth import ModelXnatAuth
from xnat_auth.view_xnat_auth import ViewXnatAuth
from xnat_auth.controller_xnat_auth import ControllerXnatAuth


class AppModules:
    def __init__(self, page):
        # MAIN
        self.model_main = ModelMainInterface()
        self.view_main = ViewMainInterface(page)
        self.controller_main = ControllerMainInterface(self.view_main,
                                                       self.model_main)
        self.view_main.set_controller(self.controller_main)
        self.controls_main = self.view_main.build_interface()

        # CONVERTER
        self.model_converter = ModelConverter()
        self.view_converter = ViewConverter(page)
        self.controller_converter = ControllerConverter(
            self.view_converter, self.model_converter
        )
        self.view_converter.set_controller(self.controller_converter)
        self.controls_converter = self.view_converter.build_interface()

        # UPLOADER
        self.model_uploader = ModelUploader()
        self.view_uploader = ViewUploader(page)
        self.controller_uploader = ControllerUploader(
            self.view_uploader, self.model_uploader
        )
        self.view_uploader.set_controller(self.controller_uploader)
        self.controls_uploader = self.view_uploader.build_interface()

        # CUSTOM FORM
        self.model_custom_form = ModelCustomForm()
        self.view_custom_form = ViewCustomForm(page)
        self.controller_custom_form = ControllerCustomForm(
            self.view_custom_form, self.model_custom_form
        )
        self.view_custom_form.set_controller(self.controller_custom_form)
        self.controls_custom_form = self.view_custom_form.build_interface()

        # XNAT AUTH
        self.model_xnat_auth = ModelXnatAuth()
        self.view_xnat_auth = ViewXnatAuth(page)
        self.controller_xnat_auth = ControllerXnatAuth(
            self.view_xnat_auth, self.model_xnat_auth
        )
        self.view_xnat_auth.set_controller(self.controller_xnat_auth)

        # Link uploader → XNAT Auth
        self.controller_uploader.set_xnat_auth(
            self.view_xnat_auth, self.controller_xnat_auth
        )

        # Link custom form → XNAT Auth
        self.controller_custom_form.set_xnat_auth(
            self.view_xnat_auth, self.controller_xnat_auth
        )

