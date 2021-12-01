#!/home/xnat/anaconda3/envs/py3/bin/python3.7
# -*- coding: utf-8 -*-
"""
Created on Mar 1, 2019

@author: Sara Zullino, Alessandro Paglialonga
"""
import shutil, os
import xnat
from glob import glob
from tkinter import messagebox
import re
import datetime
import pydicom
import sys
import traceback
import tkinter as tk
from tkinter import filedialog

# from tkinter import ttk


def xnat_uploader(folder_to_convert, project_id, num_cust_vars, address, user, psw):

    try:
        flag = 1
        path = folder_to_convert

        ## FIND DEPTH OF SUBJECT FOLDER ##
        for root, dirs, files in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)

            for file in files:
                if re.match("([^^]|[a-z]|[A-Z]|[0-9])*$", file):
                    flag = flag & 1
                else:
                    flag = flag & 0
            if flag == 1:
                subject_depth = depth - 3
                if subject_depth < 0:
                    subject_depth = 0
                del dirs
                dirs = []
                dirs[:] = []
        for root, dirs, files in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)
            if subject_depth == depth:
                for subject_dir in dirs:
                    path = root
                    custom_vars = []
                    custom_values = []
                    for x in range(0, num_cust_vars):
                        custom_values.append(os.path.basename(path))
                        path = os.path.dirname(path)
                        custom_vars.append(os.path.basename(path))
                        path = os.path.dirname(path)
                    custom_vars = custom_vars[::-1]
                    custom_values = custom_values[::-1] 
                    #######################################
                    # Problem with os.path.join() function: 
                    #######################################
                    # a = root + '/' + subject_dir
                    # folder_list = sorted(glob(root + '/' + subject_dir + '/*/', recursive=True))
                    # folder_list = sorted(glob(os.path.join(root, subject_dir) + '/*/', recursive=True))
                    folder_list = sorted(glob(root + '/*/', recursive=True))
                    for item in folder_list:
                        print(item)
                        file_list = sorted(glob(item + '/*/*', recursive=True))
                        print(file_list[0])                   
                        try:
                            ds = pydicom.dcmread(file_list[0])
                            print("subject_dir", subject_dir)
                            subject_id = subject_dir.split('.')[0]  # remove .xyz in subject_id
                            print("subject_id is ", subject_id)
                            if '.' in ds.StudyTime:                           
                                ds.StudyTime = ds.StudyTime.split('.',1)[0]
                            ds.StudyTime = "_".join(ds.StudyTime.split('.'))
                            ds.StudyDate = "_".join(ds.StudyDate.split('.'))
                            if ds.StudyDate != "" and ds.StudyTime != "":
                                experiment_id = (
                                    subject_id + "_" + ds.StudyDate + "_" + ds.StudyTime
                                )
    
                            else:
                                experiment_id = (
                                    subject_id
                                    + "_"
                                    + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                )
                            for var in custom_values:
                                experiment_id += "_" + var
                            print(experiment_id)
                            try:
                                with xnat.connect(address, user, psw) as session:
                                    zip_dst = shutil.make_archive(subject_id, "zip", item)
                                    project = session.classes.ProjectData(
                                    name=project_id, parent=session
                                    )
                                    subject = session.classes.SubjectData(
                                        parent=project, label=subject_id
                                    )
                                    session.services.import_(
                                        zip_dst,
                                        overwrite="none",
                                        project=project_id,
                                        subject=subject_id,
                                        experiment=experiment_id,
                                    )
                                    subject = project.subjects[subject_id]
                                    ########
                                    exp = project.subjects[subject_id].experiments[
                                        experiment_id
                                    ]
                                    ########
                                    for i, element in enumerate(custom_vars):
                                        subject.fields[element] = custom_values[i]
                                        exp.fields[element] = custom_values[i]
                                        print("custom values ",custom_values[i])
                                    os.remove(zip_dst)
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC - Uploader", e)
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                traceback.print_tb(exc_traceback)
                                sys.exit(1)
                        except Exception as errr:
                            messagebox.showerror("XNAT-PIC - Uploader", errr)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_tb(exc_traceback)
                            sys.exit(1)

        answer = messagebox.askyesno(
            "XNAT-PIC - Bruker2DICOM", "Do you want to upload your Bruker data to XNAT?"
        )
                
        if answer is True:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            bruker_folder = filedialog.askdirectory(parent=root,initialdir=os.path.expanduser("~"),\
                                                    title='Please select Bruker files directory')
            print(bruker_folder)
            session = xnat.connect(address, user, psw)
            rsc_label = 'bruker_data'
            project = session.classes.ProjectData(name=project_id, parent=session)
            resource = session.classes.ResourceCatalog(parent=project, label=rsc_label)          
            zip_bruker = shutil.make_archive(os.path.basename(bruker_folder), 'zip', bruker_folder)
            print(zip_bruker)
            resource.upload(zip_bruker, project_id, overwrite=True, extract=True) 
            print('Uploaded')
            os.remove(zip_bruker)           
            session.disconnect()
    

        ########
        messagebox.showinfo(
            "XNAT-PIC - Uploader", "DICOM images have been successfully imported to XNAT!"
        )

        # os._exit(0)

    except Exception as err:
        messagebox.showerror("XNAT-PIC - Uploader", err)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        # session.disconnect()
        sys.exit(1)   