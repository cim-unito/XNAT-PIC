from glob import glob
from pydicom import dcmread
from pydicom.uid import UID, generate_uid, ExplicitVRLittleEndian
from pydicom.dataset import FileMetaDataset
import threading
import tkinter as tk
import ttkbootstrap as ttk

from accessory_functions import *
from progress_bar import ProgressBar

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"
SMALL_FONT_2 = ("Calibri", 10)

class NewDataTypeProjectManager():
    def __init__(self, root, working_folder):
        self.root = root
        self.current_item = None
        self.current_column = None
        self.working_folder = working_folder

        self.setup_popup()
        self.setup_treeview()
        self.setup_combobox()
        self.setup_buttons()

        try:
            self.populate_table_view()
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading files: {e}") from e

    def setup_popup(self):
        # Load icon
        self.add_icon = open_image(PATH_IMAGE + "add_icon.png", 30, 30)
        
        # Define popup to create a new project
        self.popup_dicom_prj = ttk.Toplevel()
        self.popup_dicom_prj.title("XNAT-PIC ~ Imaging Modality")

        screen_width = self.popup_dicom_prj.winfo_screenwidth()
        screen_height = self.popup_dicom_prj.winfo_screenheight()

        width = screen_width // 2
        height = screen_height // 2

        # posizione x, y per centrare la finestra
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.popup_dicom_prj.geometry(f"{width}x{height}+{x}+{y}")

        #root.eval(f'tk::PlaceWindow {str(self.popup_dicom_prj)} center')
        #self.popup_dicom_prj.resizable(False, False)
        self.popup_dicom_prj.grab_set()
        # If you want the logo 
        self.popup_dicom_prj.iconbitmap(PATH_IMAGE + "logo3.ico")
        self.popup_dicom_prj.grid_columnconfigure(0, weight=1)
        self.popup_dicom_prj.grid_rowconfigure(0, weight=1)

    def setup_treeview(self):
        self.columns = ("Id", "Subject","Experiment", "Modality")
        self.tree = ttk.Treeview(self.popup_dicom_prj, columns=self.columns, show="headings", height=6, style="primary")
        self.tree.heading("Id", text="Id")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Experiment", text="Experiment")
        self.tree.heading("Modality", text="Modality")
        # self.tree.column("Id", width=150)
        # self.tree.column("Subject", width=150)
        # self.tree.column("Experiment", width=150)
        # self.tree.column("Modality", width=150)
        self.tree.bind("<Button-1>", self.on_cell_click)
        self.tree.grid(row=0, column=0, sticky="nsew")

        
        # Scrollbar verticale
        self.tree_scrollbar = ttk.Scrollbar(self.popup_dicom_prj, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Collego scrollbar e treeview
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

    def setup_combobox(self):
        self.combo = ttk.Combobox(self.tree, values=["CT", "MR", "OI", "OT", "PET"])
        self.combo.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.combo.place_forget()
    
    def setup_buttons(self):
        
        # Closing window event: if it occurs, the popup must be destroyed 
        def closed_window():
            self.popup_dicom_prj.destroy()
        self.popup_dicom_prj.protocol("WM_DELETE_WINDOW", closed_window)

        # Button Save
        self.popup_dicom_prj.button_save = ttk.Button(self.popup_dicom_prj, text = 'Save', command = lambda: self.save_prj(), 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_dicom_prj.button_save.grid(row=1, column=0, padx=10, pady=5, sticky=tk.NE)

        # Button Quit
        self.popup_dicom_prj.button_quit = ttk.Button(self.popup_dicom_prj, text = 'Quit', command=closed_window, 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_dicom_prj.button_quit.grid(row=1, column=0, padx=10, pady=5, sticky=tk.NW)
    
    def on_combobox_select(self, event):
        selected_value = self.combo.get()
        if self.current_item and self.current_column:
            self.tree.set(self.current_item, column=self.current_column, value=selected_value)
        self.combo.place_forget()

    def on_cell_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            self.combo.place_forget()
            return

        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if column != "#4":  # Only show combobox in "Modality" column
            self.combo.place_forget()
            return

        bbox = self.tree.bbox(item, column)
        if not bbox:
            self.combo.place_forget()
            return

        x, y, width, height = bbox
        self.combo.place(x=x, y=y, width=width, height=height)
        self.combo.focus()

        # Set current context
        self.current_item = item
        self.current_column = column

        current_value = self.tree.set(item, column=column)
        self.combo.set(current_value if current_value in self.combo['values'] else '')

    def check_dicom(self, path_dicom):
        # Check that all dicom files inside the experiment have valid dicom headers
        for path in path_dicom:
            ds = dcmread(path)
            # Meta info
            if not hasattr(ds, 'file_meta') or ds.file_meta is None:
                ds.file_meta = FileMetaDataset()

           # SOP Class UID per Raw Data Storage
            if not hasattr(ds.file_meta, 'MediaStorageSOPClassUID') or ds.file_meta.MediaStorageSOPClassUID is None:
                ds.file_meta.MediaStorageSOPClassUID = UID("1.2.840.10008.5.1.4.1.1.66")  # Raw Data Storage

            if not hasattr(ds, 'SOPClassUID') or ds.SOPClassUID is None:
                ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID

            # SOP Instance UID
            if not hasattr(ds, 'SOPInstanceUID') or ds.SOPInstanceUID is None:
                ds.SOPInstanceUID = generate_uid()
            if not hasattr(ds.file_meta, 'MediaStorageSOPInstanceUID') or ds.file_meta.MediaStorageSOPInstanceUID is None:
                ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

            # Transfer Syntax
            if not hasattr(ds.file_meta, 'TransferSyntaxUID') or ds.file_meta.TransferSyntaxUID is None:
                ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

            # Tag fissi
            if not hasattr(ds, 'PatientID') or ds.PatientID is None:
                ds.PatientID = str(os.path.basename(os.path.dirname(os.path.dirname(path))))
            if not hasattr(ds, 'StudyInstanceUID') or ds.StudyInstanceUID is None:
                ds.StudyInstanceUID = generate_uid()
            if not hasattr(ds, 'SeriesInstanceUID') or ds.SeriesInstanceUID is None:
                ds.SeriesInstanceUID = generate_uid()
            if not hasattr(ds, 'Modality') or ds.Modality is None:
                ds.Modality = "OT"

            ds.save_as(path, write_like_original=False)
            
        
    def read_dicom(self, path_dicom):
        ds = dcmread(path_dicom)
        return ds.Modality if getattr(ds, 'Modality', None) else "OT"

    def populate_table_view(self):

        # Scan the folder to get its tree
        subdir = os.listdir(self.working_folder)
        # Check for OS configuration files and remove them
        subdirectories = [x for x in subdir if x.endswith('.ini') == False]
        # Dict of subjects and experiments in the project to upload
        dict_exp = {}
        j = 0
        for sub in subdirectories:
            if os.path.isdir(os.path.join(self.working_folder, sub)):
                # Scansiona le directory interne 
                sub_level2 = os.listdir(os.path.join(self.working_folder, sub))
                subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                for sub2 in subdirectories2:
                    if os.path.isdir(os.path.join(self.working_folder, sub, sub2)):
                        tmp_exp_path = os.path.join(self.working_folder, sub, sub2)
                        list_dcm = glob(tmp_exp_path + "/**/*.dcm", recursive=False)
                        list_dicom = glob(tmp_exp_path + "/**/*.dicom", recursive=False)
                        if (list_dcm or list_dcm):
                            modality = self.read_dicom((list_dcm or list_dicom)[0])
                            dict_exp[j] = [sub, sub2, tmp_exp_path, modality]
                            j += 1

        print(dict_exp)

        for k, v in dict_exp.items():
            self.tree.insert("", 'end', values=[str(k), str(v[0]), str(v[1]), str(v[3])])
        
        messagebox.showinfo("XNAT-PIC", 'The DICOM files have been updated!')
        #self.popup_dicom_prj.destroy()