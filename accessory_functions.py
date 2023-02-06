# -*- coding: utf-8 -*-
"""
Created on May 30, 2022

@author: Riccardo Gambino

"""
import os
import pandas as pd
from tabulate import tabulate
from PIL import Image, ImageTk
from read_visupars import read_visupars_parameters
import pydicom
import datetime 
import datefinder
import time

# Accessory functions
def disable_buttons(list_of_buttons):
    for btn in list_of_buttons:
        try:
            btn.configure(state="disabled")
        except:
            pass

def enable_buttons(list_of_buttons):
    for btn in list_of_buttons:
        try:
            btn.configure(state="normal")
        except:
            pass

def destroy_widgets(widgets):
    for widget in widgets:
        try:
            widget.destroy()
        except:
            pass

def delete_widgets(canva, widgets_id):
    for id in widgets_id:
        try:
            canva.delete(id)
        except:
            pass

def get_dir_size(path):

    total_weight = 0
    if os.path.isdir(path):
        for l, level1 in enumerate(os.listdir(path)):
            if os.path.isfile(os.path.join(path, level1)):
                total_weight += os.path.getsize(os.path.join(path, level1))
            elif os.path.isdir(os.path.join(path, level1)):
                for m, level2 in enumerate(os.listdir(os.path.join(path, level1))):
                    if os.path.isfile(os.path.join(path, level1, level2)):
                        total_weight += os.path.getsize(os.path.join(path, level1, level2))
                    elif os.path.isdir(os.path.join(path, level1, level2)):
                        for n, level3 in enumerate(os.listdir(os.path.join(path, level1, level2))):
                            if os.path.isfile(os.path.join(path, level1, level2, level3)):
                                total_weight += os.path.getsize(os.path.join(path, level1, level2, level3))
                            elif os.path.isdir(os.path.join(path, level1, level2, level3)):
                                for p, level4 in enumerate(os.listdir(os.path.join(path, level1, level2, level3))):
                                    if os.path.isfile(os.path.join(path, level1, level2, level3, level4)):
                                        total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4))
                            #         elif os.path.isdir(os.path.join(path, level1, level2, level3,level4)):
                            #             for q, level5 in enumerate(os.listdir(os.path.join(path, level1, level2, level3, level4))):
                            #                 if os.path.isfile(os.path.join(path, level1, level2, level3, level4, level5)):
                            #                     total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4, level5))
                            #                 elif os.path.isdir(os.path.join(path, level1, level2, level3,level4, level5)):
                            #                     for q, level6 in enumerate(os.listdir(os.path.join(path, level1, level2, level3, level4, level5))):
                            #                         if os.path.isfile(os.path.join(path, level1, level2, level3, level4, level5, level6)):
                            #                             total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4, level5, level6))


        return round(total_weight, 2)
    else:
        return 0

def read_table(path_to_read):

    data_dict = {}
    data = pd.read_table(path_to_read, delimiter='\s\s+', header=[0], skiprows=1,
        dtype={'Variable': str}, engine='python').values.tolist()
    for elem in data:
        data_dict[elem[0]] = elem[1]
    return data_dict

def write_table(path_to_write, edit):

    try:
        # If there is already a file, edit it
        data = read_table(path_to_write)
        for j in edit.keys():
            for k in data.keys():
                if j == k:
                    data[k] = edit[j]
        with open(path_to_write.replace('\\', '/'), 'w+') as out_file:
            out_file.write(tabulate(data.items(), headers=['Variable', 'Value']))
    except:
        # If the file does not exist yet
        with open(path_to_write.replace('\\', '/'), 'w+') as out_file:
            # out_file.write(tabulate(info.items(), headers=['Variable', 'Value']))
            out_file.write(tabulate(edit.items(), headers=['Variable', 'Value']))

def open_image(path, width=0, height=0):

    image = Image.open(path).convert("RGBA")
    if width != 0 or height != 0:
        image = image.resize((int(width), int(height)), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    return image

#Read the acq. date from visu_pars file for Bruker file or from DICOM files
def read_acq_date(path): 
    match_date = ''
    for dirpath, dirnames, filenames in os.walk(path.replace('\\', '/')):
        # Check if the visu pars file is in the scans
        for filename in [f for f in filenames if f.startswith("visu_pars")]:
            acq_date = read_visupars_parameters((dirpath + "\\" + filename).replace('\\', '/'))["VisuAcqDate"]
            # Read the date
            matches = datefinder.find_dates(str(acq_date))
            for match in matches:
                match_date = match.strftime('%Y-%m-%d')
                return match_date
        # Check if the DICOM is in the scans
        for filename in [f for f in filenames if f.endswith(".dcm")]:
            dataset = pydicom.dcmread((dirpath + "\\" + filename).replace('\\', '/'))
            match_date = datetime.datetime.strptime(dataset.AcquisitionDate, '%Y%m%d').strftime('%Y-%m-%d')
            return match_date
    return match_date

def metadata_params(information_folder, value):
    # If value = 0 --> project
    # If value = 1 --> subject
    # If value = 2 --> experiment
    
    if value == 0:
        tmp_dict = {}
        results_dict = {}
            
        # Get a list of workbook paths 
        path_list = []
        todos = {}
        todos_tmp = {}
        exp = []
        # Scan all files contained in the folder that the user has provided
        for item in os.listdir(information_folder):
            path = str(information_folder + "\\" + item).replace('\\', '/')
            # Check if the content of the project is a folder and therefore a patient or a file not to be considered
            if os.path.isdir(path):
                # Architecture of the project: project-subject-experiment
                for item2 in os.listdir(path):
                    path1 = str(path + "\\" + item2).replace('\\', '/')
                    if os.path.isdir(path1):
                        path_list.append(path1)
                        exp.append(str(item2))
                todos_tmp = {item: exp}
                exp = []
            todos.update(todos_tmp)
            todos_tmp = {}

    elif value == 1:
        tmp_dict = {}
        results_dict = {}
        sub = str(information_folder).rsplit("/",1)[1]

        # Get a list of workbook paths 
        path_list = []
        todos = {}
        exp = []
        # Scan all files contained in the folder that the user has provided
        for item in os.listdir(information_folder):
            path = str(information_folder + "\\" + item).replace('\\', '/')
            # Check if the content of the subject is a folder and therefore a patient or a file not to be considered
            if os.path.isdir(path):
                # Architecture of the project: project-subject-experiment
                if os.path.isdir(path):
                    path_list.append(path)
                    exp.append(str(item))
        todos = {sub : exp}
        
    elif value == 2:
        tmp_dict = {}
        results_dict = {}

        # Get a list of workbook paths 
        path_list = [information_folder]
        todos = {str(information_folder).rsplit("/",3)[2] : [str(information_folder).rsplit("/",3)[3]]}
    
    path_list1 = {}
    # Scan all files contained in the folder that the user has provided
    for path in path_list:
        exp = str(path).rsplit("/",3)[3]
        sub = str(path).rsplit("/",3)[2]
        prj = str(path).rsplit("/",3)[1]
        name = exp + "_" + "Custom_Variables.txt"
        keys = sub + "#" + exp
        path_list1.update({keys : path})
        # Check if the txt file is in folder of the patient
        tmp_path = ''
        for dirpath, dirnames, filenames in os.walk(path.replace('\\', '/')):
            # Check if the visu pars file is in the scans
            for filename in [f for f in filenames if f.startswith("visu_pars")]:
                tmp_path = path
                break
            # Check if the DICOM is in the scans
            for filename in [f for f in filenames if f.endswith(".dcm")]:
                tmp_path = path + "\\MR\\"
                break
            if tmp_path:
                break
        # If the file exists, read le info
        if os.path.exists((tmp_path + "\\" + name).replace('\\', '/')):
            subject_data = read_table((tmp_path + "\\" + name).replace('\\', '/'))
            tmp_dict = {keys: subject_data}
        else:
        # If the txt file do not exist, load default value
        # Project: name of main folder
        # Subject: name of internal folders
        # Acq date: from visu_pars file for BRUKER, from DICOM from DICOM file
        #
        # Load the acq. date for BRUKER file
            try:
                tmp_acq_date = read_acq_date(path)
            except Exception as e:
                tmp_acq_date = ''
            
            subject_data = {"Project": prj,
                        "Subject": sub,
                        "Experiment": exp,
                        "Acquisition_date": tmp_acq_date,
                        "C_V": "",
                        "Group": "",
                        "Timepoint":"",
                        "Dose":""
                        }
            tmp_dict = {keys: subject_data}

        results_dict.update(tmp_dict)

    return [results_dict, todos, path_list, path_list1]

def write_tree(folder_path):
    dict_items = {}
    j = 0
    dict_items[str(j)] = {}
    dict_items[str(j)]['parent'] = ""
    dict_items[str(j)]['text'] = folder_path.split('/')[-1]

    subdir = os.listdir(folder_path)
    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
    total_weight = 0
    last_edit_time = ''
    j = 1
    for sub in subdirectories:
        
        if os.path.isfile(os.path.join(folder_path, sub)):
            # Check for last edit time
            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(folder_path, sub)))))
            if last_edit_time == '' or edit_time > last_edit_time:
                # Update the last edit time
                last_edit_time = edit_time
            # Check for file dimension
            file_weight = round(os.path.getsize(os.path.join(folder_path, sub))/1024, 2)
            total_weight += round(file_weight/1024, 2)
            # Add the item like a file
            dict_items[str(j)] = {}
            dict_items[str(j)]['parent'] = '0'
            dict_items[str(j)]['text'] = sub
            dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
            # Update the j counter
            j += 1

        elif os.path.isdir(os.path.join(folder_path, sub)):
            current_weight = 0
            last_edit_time_lev2 = ''
            branch_idx = j
            dict_items[str(j)] = {}
            dict_items[str(j)]['parent'] = '0'
            dict_items[str(j)]['text'] = sub
            j += 1
            # Scan directories to get subfolders
            sub_level2 = os.listdir(os.path.join(folder_path, sub))
            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
            for sub2 in subdirectories2:
                if os.path.isfile(os.path.join(folder_path, sub, sub2)):
                    # Check for last edit time
                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(folder_path, sub, sub2)))))
                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                        # Update the last edit time
                        last_edit_time_lev2 = edit_time
                    if last_edit_time_lev2 > last_edit_time:
                        last_edit_time = last_edit_time_lev2
                    # Check for file dimension
                    file_weight = round(os.path.getsize(os.path.join(folder_path, sub, sub2))/1024, 2)
                    current_weight += round(file_weight/1024, 2)
                    # Add the item like a file
                    dict_items[str(j)] = {}
                    dict_items[str(j)]['parent'] = '1'
                    dict_items[str(j)]['text'] = sub2
                    dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                    # Update the j counter
                    j += 1

                elif os.path.isdir(os.path.join(folder_path, sub, sub2)):
                    # Check for last edit time
                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(folder_path, sub, sub2)))))
                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                        # Update the last edit time
                        last_edit_time_lev2 = edit_time
                    if last_edit_time_lev2 > last_edit_time:
                        last_edit_time = last_edit_time_lev2

                    folder_size = round(get_dir_size(os.path.join(folder_path, sub, sub2))/1024/1024, 2)
                    current_weight += folder_size
                    dict_items[str(j)] = {}
                    dict_items[str(j)]['parent'] = '1'
                    dict_items[str(j)]['text'] = sub2
                    dict_items[str(j)]['values'] = (edit_time, str(folder_size) + 'MB', "Folder")
                    j += 1
                
            total_weight += current_weight
            dict_items[str(branch_idx)]['values'] = (last_edit_time_lev2, str(round(current_weight, 2)) + "MB", "Folder")

    # Update the fields of the parent object
    dict_items['0']['values'] = (last_edit_time, str(round(total_weight/1024, 2)) + "GB", "Folder")
    return dict_items
