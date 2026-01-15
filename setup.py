import os
import sys
from importlib.util import find_spec
from cx_Freeze import setup, Executable

# python setup.py bdist_msi

company_name = 'Unito'
product_name = 'XNAT-PIC'
TARGETDIR=r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name)

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "XNAT-PIC",               # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]main.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
     ("ProgramMenuFolderShortcut",       # Shortcut
     "ProgramMenuFolder",                # Directory_
     "XNAT-PIC",                         # Name
     "TARGETDIR",                        # Component_
     "[TARGETDIR]main.exe",          # Target
     None,                               # Arguments
     None,                               # Description
     None,                               # Hotkey
     None,                               # Icon
     None,                               # IconIndex
     None,                               # ShowCmd
     'TARGETDIR'                         # WkDir
     )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

bdist_msi_options = {
    'upgrade_code': '{48B079F4-B598-438D-A62A-8A233A3F8901}',
    'add_to_path': True,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
    'data': msi_data
}

include_files = [
    ("app_modules", "app_modules"),
    ("assets", "assets"),
    ("converter", "converter"),
    ("custom_form", "custom_form"),
    ("database", "database"),
    ("enums", "enums"),
    ("main_interface", "main_interface"),
    ("route", "route"),
    ("shared_ui", "shared_ui"),
    ("uploader", "uploader"),
    ("xnat_auth", "xnat_auth"),
    ("xnat_client", "xnat_client"),
]

xnat_spec = find_spec("xnat")
if xnat_spec and xnat_spec.submodule_search_locations:
    xnat_pkg_dir = next(iter(xnat_spec.submodule_search_locations), None)
    if xnat_pkg_dir:
        header_path = os.path.join(xnat_pkg_dir, "header.py")
        if os.path.exists(header_path):
            include_files.append((header_path, os.path.join("lib", "xnat", "header.py")))

build_exe_options = {
    "packages": ["flet"],
    "include_files": include_files,
}


# GUI applications require a different base on Windows
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

exe = Executable(script='main.py',
base=base,
#icon="logo3.ico"
#hortcut_name="XNAT-PIC",
#shortcut_dir=["DesktopFolder", "ProgramMenuFolder"]
#shortcut_dir="ProgramMenuFolder"
)

setup(name=product_name,
version='2.0.0',
description='XNAT for Preclinical Imaging Centers (XNAT-PIC) has been developed to expand basic functionalities of XNAT to preclinical imaging',
executables=[exe],
options={'bdist_msi': bdist_msi_options,
'build_exe': build_exe_options})