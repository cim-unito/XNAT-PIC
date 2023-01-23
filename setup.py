import sys
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
     "[TARGETDIR]launcher.exe",# Target
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
     "[TARGETDIR]launcher.exe",          # Target
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

build_exe_options = {
    "packages": ['ttkbootstrap'],
    'include_files': [("layout_colors.json", ""), ("images", ""), ("tcl", "./lib/tkinter")]
}


# GUI applications require a different base on Windows
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

exe = Executable(script='launcher.py',
base=base,
icon="logo3.ico"
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