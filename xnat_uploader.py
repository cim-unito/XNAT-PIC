# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
# import threading
from numpy import empty
# import pandas as pd
import os
from tkinter import messagebox
import xnat, shutil, time
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, process

class Dicom2XnatUploader():

    def __init__(self, session):

        self.session = session
        self.n_processes = int(cpu_count() - 1)

    def multi_core_upload(self, folder_to_upload, project_id):

        list_dirs = os.listdir(folder_to_upload)
        list_of_subjects = [(os.path.join(folder_to_upload, sub).replace('\\', '/'), project_id) for sub in list_dirs]

        start_time = time.time()

        with Pool(processes = self.n_processes) as pool:
            pool.map(self.upload, list_of_subjects)

        end_time = time.time()
        print('Elapsed time for conversion: ' + str(end_time - start_time) + ' s')

    def single_core_upload(self, folder_to_upload, project_id, master):

        list_dirs = os.listdir(folder_to_upload)
        list_of_subjects = [(os.path.join(folder_to_upload, sub).replace('\\', '/'), project_id) for sub in list_dirs]

        start_time = time.time()

        for sub in list_of_subjects:
            self.upload(sub, master)

        end_time = time.time()
        print('Elapsed time for conversion: ' + str(end_time - start_time) + ' s')

    def upload(self, params):
    
        try:
            folder_to_upload = params['folder_to_upload']
            project_id = params['project_id']
            subject_id = params['subject_id']
            experiment_id = params['experiment_id']
            flag = params['custom_var_flag']

            print('Uploading ' + str(folder_to_upload.split('/')[-2]) + ' to ' + str(project_id))

            project = self.session.classes.ProjectData(
                                            name=project_id, parent=self.session)
            subject = self.session.classes.SubjectData(
                                            parent=project, label=subject_id)


            zip_dst = shutil.make_archive(folder_to_upload.split('/')[-2], "zip", folder_to_upload) # .zip file of the current subfolder

            self.session.services.import_(zip_dst,
                                        overwrite="delete", # Overwrite parameter is important!
                                        project=project_id,
                                        subject=subject_id,
                                        experiment=experiment_id,
                                        content_type='application/zip')
            self.session.clearcache()
            experiment = self.session.projects[project_id].subjects[subject_id].experiments[experiment_id]
            subject = self.session.projects[project_id].subjects[subject_id]

            print('Updating ' + str(flag) + ' custom variables...')
            count = 0
            for var in params.keys():
                if var not in ['project_id', 'subject_id', 'folder_to_upload', 'experiment_id', 'custom_var_flag', 'SubjectsCV', 'SubjectsGroup', 'SubjectsTimepoint',
                                'SubjectsDose', 'SessionsCV']:
                    expfield = var.replace('Sessions', '')           
                    experiment.fields[expfield.lower()] = params[var]
                if var not in ['project_id', 'subject_id', 'folder_to_upload', 'experiment_id', 'custom_var_flag', 'SubjectsCV', 'SessionsGroup', 'SessionsTimepoint',
                                'SessionsDose', 'SessionsCV']:
                    subfield = var.replace('Subjects', '') 
                    subject.fields[subfield.lower()] = params[var]
                    count += 1

            os.remove(zip_dst)

        except Exception as e: 
            messagebox.showerror("XNAT-PIC - Uploader", e)
            try:
                os.remove(zip_dst)
            except: 
                pass

class FileUploader():

    def __init__(self, session):

        self.session = session
        self.n_processes = int(cpu_count() -1)

    def upload(self, list_of_files, params):

        def upload_file(url, data):
            try:
                self.session.put(path=url, files=data)
                print("Uploaded " + url.split('/')[-1])
            except Exception as e:
                print("NOT Uploaded " + url.split('/')[-1])
                messagebox.showerror("XNAT-PIC - Uploader", e)

        print('Loading additional files for experiment: ' + str(params['experiment_id']))

        file_urls = []
        file_data = []
        for i, file in enumerate(list_of_files, 1):
            if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.mat', '.fig', '.pdf', '.xlsx', '.txt')):
                current_path_file = file.replace('\\', '/')
                
                test_project = self.session.projects[params['project_id']]
                test_subjects = test_project.subjects[params['subject_id']]
                test_exp = test_subjects.experiments[params['experiment_id']]
                test_resources = test_exp.resources

                file_name = str(os.path.splitext(current_path_file.split('/')[-1])[0]).replace(' ', '_').replace('-', '_').replace('.', '_').replace('__', '_').rstrip('_')
                file_ext = str(os.path.splitext(current_path_file.split('/')[-1])[-1])
                file_urls.append(test_resources.uri + '/' + str(params['folder_name']) + 
                            '/files/' + file_name + file_ext)

                with open(current_path_file, 'rb') as f:
                    img = f.read()
                file_data.append({"1": img})

        try:
            # for j, url in enumerate(file_urls):
            #     upload_file(url, file_data[j])
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.map(upload_file, file_urls, file_data)
        except Exception as e:
            print(str(e))

    
