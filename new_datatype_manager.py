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
        self.dict_exp = {}
        self.dict_exp_changed = {}
        self.working_folder = working_folder

        self.setup_popup()
        self.setup_treeview()
        self.setup_combobox()
        self.setup_buttons()

        try:
            self.populate_tree_view()
        except Exception as e:
            messagebox.showerror('XNAT-PIC Uploader', str(e))
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
        self.tree = ttk.Treeview(self.popup_dicom_prj, columns=self.columns, show="headings", height=10, style="secondary")
        self.tree.heading("Id", text="Id", anchor=tk.CENTER)
        self.tree.heading("Subject", text="Subject", anchor=tk.CENTER)
        self.tree.heading("Experiment", text="Experiment", anchor=tk.CENTER)
        self.tree.heading("Modality", text="Modality", anchor=tk.CENTER)
        self.tree.column("Id", width=50, anchor=tk.CENTER)
        self.tree.column("Subject", width=300, anchor=tk.CENTER)
        self.tree.column("Experiment", width=300, anchor=tk.CENTER)
        self.tree.column("Modality", width=80, anchor=tk.CENTER)
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
        
    def read_dicom(self, path_dicom):
        ds = dcmread(path_dicom)
        return getattr(ds, 'Modality', None) 

    def populate_tree_view(self):

        # Scan the folder to get its tree
        subdir = os.listdir(self.working_folder)
        # Check for OS configuration files and remove them
        subdirectories = [x for x in subdir if x.endswith('.ini') == False]
        # Dict of subjects and experiments in the project to upload
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
                        if (list_dcm or list_dicom):
                            modality = self.read_dicom((list_dcm or list_dicom)[0])
                            self.dict_exp[str(j)] = [sub, sub2, tmp_exp_path, modality]
                            j += 1

        for k, v in self.dict_exp.items():
            self.tree.insert("", 'end', values=[str(k), str(v[0]), str(v[1]), str(v[3]) if v[3] is not None else "OT"])
    

    # Helper per controllare se un attributo esiste ed è non nullo
    def has_tag(self, obj, tag):
        return getattr(obj, tag, None) is not None

    # Controlla se un dataset è completo
    def is_dataset_complete(self, ds):
        return all([
            self.has_tag(ds.file_meta, 'MediaStorageSOPClassUID'),
            self.has_tag(ds.file_meta, 'MediaStorageSOPInstanceUID'),
            self.has_tag(ds.file_meta, 'TransferSyntaxUID'),
            self.has_tag(ds, 'SOPClassUID'),
            self.has_tag(ds, 'SOPInstanceUID'),
            self.has_tag(ds, 'PatientID'),
            self.has_tag(ds, 'StudyInstanceUID'),
            self.has_tag(ds, 'SeriesInstanceUID'),
            self.has_tag(ds, 'Modality'),
        ])

    # Aggiorna dataset con UID comuni
    def update_dataset(self, ds, patient_id, study_uid, series_uid, modality):
        ds.file_meta = ds.file_meta or FileMetaDataset()

        ds.file_meta.MediaStorageSOPClassUID = ds.file_meta.get('MediaStorageSOPClassUID') or UID("1.2.840.10008.5.1.4.1.1.66")
        ds.SOPClassUID = ds.get('SOPClassUID') or ds.file_meta.MediaStorageSOPClassUID

        ds.SOPInstanceUID = ds.get('SOPInstanceUID') or generate_uid()
        ds.file_meta.MediaStorageSOPInstanceUID = ds.file_meta.get('MediaStorageSOPInstanceUID') or ds.SOPInstanceUID

        ds.file_meta.TransferSyntaxUID = ds.file_meta.get('TransferSyntaxUID') or ExplicitVRLittleEndian

        ds.PatientID = ds.get('PatientID') or patient_id
        ds.StudyInstanceUID = ds.get('StudyInstanceUID') or study_uid
        ds.SeriesInstanceUID = ds.get('SeriesInstanceUID') or series_uid
        ds.Modality = modality

        return ds

    def check_dicom(self):

        for k,v in self.dict_exp.items():
            path_dicom = str(v[2])

            dicom_files = glob(path_dicom + "/**/*.dcm", recursive=False) + glob(path_dicom + "/**/*.dicom", recursive=False)

            if not dicom_files:
                continue

            # Legge solo il primo file per decidere se elaborare
            first_ds = dcmread(dicom_files[0], stop_before_pixels=True)
            if self.is_dataset_complete(first_ds) and self.dict_exp_changed[k][2] == v[3]:
                continue  # Completo → salta

            # UID comuni generati solo se necessario
            study_uid = generate_uid()
            series_uid = generate_uid()
            patient_id = v[1]
            modality = self.dict_exp_changed[k][2]

            for path in dicom_files:
                ds = dcmread(path)
                ds = self.update_dataset(ds, patient_id, study_uid, series_uid, modality)
                ds.save_as(path, write_like_original=False)
   
   
    def save_prj(self):
        exception_container = []
        cancel_operation = {'cancelled': False}  # Flag per verificare annullamento

        def func_save_prj():
            try: 
                for item_id in self.tree.get_children():
                    val = self.tree.item(item_id, "values")
                    self.dict_exp_changed[val[0]] = val[1:]

                # Controllo se almeno una modality è 'OT'
                has_ot = any(values[2] == 'OT' for values in self.dict_exp_changed.values())

                if has_ot:
                    # Mostra un messaggio di avviso all'utente
                    proceed = messagebox.askyesno(
                        "Warning",
                        "There is at least one 'OT' modality. Continue anyway?"
                    )
                    if not proceed:
                        cancel_operation['cancelled'] = True  # Segnala annullamento
                        return  # Interrompe e torna all'interfaccia

                self.check_dicom()
            except Exception as e:
                exception_container.append(e)
            
        try:
            # Start the progress bar
            progressbar = ProgressBar(self.popup_dicom_prj, bar_title='XNAT-PIC Modality')
            progressbar.start_indeterminate_bar()
            
            # Disable button
            disable_buttons([self.popup_dicom_prj.button_save, self.popup_dicom_prj.button_quit])
            # Save the project through separate thread (different from the main thread)
            tp = threading.Thread(target=func_save_prj, args=())
            tp.start()
            while tp.is_alive() == True:
                # As long as the thread is working, update the progress bar
                progressbar.update_bar()
            progressbar.stop_progress_bar()
            
            # Controlla se l'operazione è stata annullata
            if cancel_operation['cancelled']:
                enable_buttons([self.popup_dicom_prj.button_save, self.popup_dicom_prj.button_quit])
                return  # Esce senza chiudere la finestra
        
            # Check if exception occurred
            if exception_container:
                enable_buttons([self.popup_dicom_prj.button_save, self.popup_dicom_prj.button_quit])
                raise exception_container[0]
        
            messagebox.showinfo("XNAT-PIC", 'Changes saved successfully!')
            self.popup_dicom_prj.destroy()
        except Exception as e:
            messagebox.showerror('XNAT-PIC Uploader', str(e))
            self.popup_dicom_prj.destroy()
            raise RuntimeError(f"Unexpected error while reading files: {e}") from e