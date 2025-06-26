








    def __init__(self, root

        

       

        # Add the scans of the experiment
        # Listbox experiment added
        coldata = [
            {"text": "Id", "stretch": False},
            {"text": "Subject", "stretch": False},
            {"text": "Experiment", "stretch": False},
            {"text": "Modality", "stretch": False},
        ]
        rowdata = [
        ]

        self.dt = ttk.Treeview(
            master=self.popup_dicom_prj,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=False,
            bootstyle=ttk.PRIMARY,
            height = 10
        )
        self.dt.grid(row=2, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)

        # Combobox che verrà sovrapposto
        self.combo_modality = ttk.Combobox(self.dt, values=["CT", "MR", "OI", "OT", "PET"])
        self.combo_modality.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Variabili per tracciare cella corrente
        self.current_item_id = None
        self.current_column_id = None

        # Bind evento click sulla tabella
        self.dt.bind("<Button-1>", self.on_cell_click)
            



        
    def on_cell_click(self, event):
        region = self.dt.identify("region", event.x, event.y)
        if region != "cell":
            self.combo_modality.place_forget()
            return

        row_id = self.dt.identify_row(event.y)
        column = self.dt.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        col_name = self.dt["columns"][col_index]

        # Solo colonna "Modality"
        if col_name != "Modality":
            self.combo_modality.place_forget()
            return

        bbox = self.dt.bbox(row_id, column)
        if not bbox:
            return

        x, y, width, height = bbox
        self.current_item_id = row_id
        self.current_column_id = col_name
        current_value = self.dt.set(row_id, col_name)

        self.combo_modality.set(current_value)
        self.combo_modality.place(x=x, y=y, width=width, height=height)
        self.combo_modality.focus()

    def on_combobox_select(self, event):
        selected_value = self.combo_modality.get()
        if self.current_item_id and self.current_column_id:
            self.dt.set(self.current_item_id, self.current_column_id, selected_value)
        self.combo_modality.place_forget() 

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
            self.dt.insert_row('end', [str(k), str(v[0]), str(v[1]), str(v[3])])
        self.dt.load_table_data()
        
        messagebox.showinfo("XNAT-PIC", 'The DICOM files have been updated!')
        #self.popup_dicom_prj.destroy()