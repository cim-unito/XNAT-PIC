# -*- coding: utf-8 -*-
"""
Created on May 30, 2022

@author: Riccardo Gambino

"""
from tkinter import END, messagebox
import tkinter, os, json, shutil
import ttkbootstrap as ttk
import tkinter as tk
from accessory_functions import disable_buttons, enable_buttons, open_image
from datetime import date, datetime
from logging import exception
import tkinter.simpledialog
from progress_bar import ProgressBar
import time
from idlelib.tooltip import Hovertip

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"

class ProjectManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)
        self.add_icon = open_image(PATH_IMAGE + "add_icon.png", 15, 15)

        self.master = tk.Toplevel()
        self.master.grab_set()
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)
        self.master.iconbitmap(PATH_IMAGE + "logo3.ico")

        ###########################################################################
        # Project Widgets
        ###########################################################################
        # LabelFrame for Project Info
        self.project_labelframe = ttk.LabelFrame(self.master, text="Add New Project")
        self.project_labelframe.pack(fill='x', padx=10, pady=10)
        # TITLE
        self.project_title = tk.StringVar()
        self.project_title_label = ttk.Label(self.project_labelframe, text="Project Title *")
        self.project_title_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_title_entry = ttk.Entry(self.project_labelframe, width=50, textvariable=self.project_title)
        self.project_title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        # ID
        self.project_id = tk.StringVar()
        self.project_id_label = ttk.Label(self.project_labelframe, text="Project ID *")
        self.project_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_id_labelframe = ttk.Labelframe(self.project_labelframe, style="Hidden.TLabelframe")
        self.project_id_labelframe.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NW)
        self.project_id_entry = ttk.Entry(self.project_id_labelframe, width=50, textvariable=self.project_id,
                                            state='disabled')
        self.project_id_entry.pack(fill='x', anchor=tk.W)
        self.project_id_modify = tk.IntVar()
        self.project_id_checkbutton = ttk.Checkbutton(self.project_labelframe, text="Modify", onvalue=1, 
                                        offvalue=0, variable=self.project_id_modify, cursor=CURSOR_HAND)
        self.project_id_checkbutton.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        def enable_entry(*args):
            if self.project_id_modify.get() == 1:
                self.project_id_entry.configure(state='normal')
            else:
                self.project_id_entry.configure(state='disabled')
        self.project_id_modify.trace('w', enable_entry)

        # ACCESSIBILITY
        self.access_labelframe = ttk.Labelframe(self.project_labelframe, text="", style="Hidden.TLabelframe")
        self.access_labelframe.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.access_label = ttk.Label(self.project_labelframe, text="Accessibility")
        self.access_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.access_status = tk.StringVar()
        self.private_access_btn = ttk.Radiobutton(self.access_labelframe, text="Private", variable=self.access_status,
                                                    value='private')
        self.private_access_btn.pack(side='left', expand=True, padx=0, pady=5)
        Hovertip(self.private_access_btn,'Only you and study members will be able to access study data.')
        self.protected_access_btn = ttk.Radiobutton(self.access_labelframe, text="Protected", variable=self.access_status,
                                                    value='protected')
        self.protected_access_btn.pack(side='left', expand=True, padx=0, pady=5)
        Hovertip(self.protected_access_btn,'All users will be able to see your study title and description, but only collaborators you approve will be able to analyze and download data.')
        self.public_access_btn = ttk.Radiobutton(self.access_labelframe, text="Public", variable=self.access_status,
                                                    value='public')
        self.public_access_btn.pack(side='left', expand=True, padx=0, pady=5)
        Hovertip(self.public_access_btn,'All users will be able to access study data for analysis and download.')
        self.access_status.set('private')

        # DESCRIPTION
        self.project_description_label = ttk.Label(self.project_labelframe, text="Project Description")
        self.project_description_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        self.project_description = tk.StringVar()
        self.project_description_entry = ttk.Text(self.project_labelframe, width=50, height=8)
        self.project_description_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.project_description_scrollbar = ttk.Scrollbar(self.project_labelframe, orient='vertical', 
                                                        command=self.project_description_entry.yview)
        self.project_description_scrollbar.grid(row=3, column=2, padx=0, pady=5, sticky=tk.NS)
        self.project_description_entry.configure(yscrollcommand=self.project_description_scrollbar.set)
        
        # KEYWORDS
        self.project_keywords_list = []
        current_keyword = tk.StringVar()
        keyword_to_remove = tk.StringVar()
        self.project_keywords_label = ttk.Label(self.project_labelframe, text="Keywords")
        self.project_keywords_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_keyword_labelframe = ttk.Labelframe(self.project_labelframe, style="Hidden.TLabelframe")
        self.project_keyword_labelframe.grid(row=4, column=1, padx=5, pady=0, sticky=tk.NW, columnspan=3)
        self.project_keywords_entry = ttk.Entry(self.project_keyword_labelframe, width=50, textvariable=current_keyword)
        self.project_keywords_entry.pack(side='top', fill='x', anchor=tk.NW)

        def clear_keywords(*args):
            for btn in self.project_keyword_labelframe.winfo_children():
                if btn != self.project_keywords_entry:
                    btn.destroy()

        def remove_keyword(*args):
            if keyword_to_remove.get() != "":
                for key in self.project_keywords_list:
                    if key == keyword_to_remove.get():
                        self.project_keywords_list.remove(keyword_to_remove.get())
                keyword_to_remove.set("")

        def show_keywords(*args):
            keywords = []
            buttons = []
            for i in range(len(self.project_keywords_list)):
                keywords.append(str(self.project_keywords_list[i]))
            for j in range(len(keywords)):
                buttons.append(ttk.Button(self.project_keyword_labelframe, text=keywords[j], 
                                    image=self.logo_delete, compound='right', cursor=CURSOR_HAND,
                                    command=lambda c=j: (keyword_to_remove.set(buttons[c]["text"]), buttons[c].destroy()), style="Keyword.TButton"))
                buttons[j].pack(side='left', padx=0, pady=2, anchor=tk.NW)

        def set_keyword(event):
            if event.char == '\r' and current_keyword.get() != "":
                self.project_keywords_list.append(current_keyword.get())
                clear_keywords()
                show_keywords()
                current_keyword.set("")
        self.project_keywords_entry.bind("<Key>", set_keyword)
        keyword_to_remove.trace('w', remove_keyword)

        # INVESTIGATORS
        self.project_investigator = tk.StringVar()
        try:
            self.investigators = json.loads(self.session.get(os.path.join(self.session.uri, '/xapi/investigators')).content)
            self.investigator_list = [','.join([x['firstname'], x['lastname']]) for x in self.investigators if 'firstname' in x.keys() and 'lastname' in x.keys()]
        except:
            self.investigator_list = []
        
        self.project_investigators_label = ttk.Label(self.project_labelframe, text="Investigators")
        self.project_investigators_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_investigators_entry = ttk.OptionMenu(self.project_labelframe, self.project_investigator, "--",
                                                             *self.investigator_list)
        self.project_investigators_entry.config(width=45, cursor=CURSOR_HAND)
        self.project_investigators_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

        self.project_investigator_newicon = ttk.Button(self.project_labelframe, image=self.add_icon, style="WithoutBack.TButton", 
                                                        cursor=CURSOR_HAND, command=self.add_new_investigator)
        self.project_investigator_newicon.grid(row=6, column=3, pady=5, sticky=tk.W)

        # Callbacks
        def title_callback(*args):
            if self.project_title.get() != '':
                self.project_id.set(self.project_title.get())
        self.project_title.trace('w', title_callback)

        def enable_submit(*args):
            if self.project_id.get() != '':
                if self.project_id.get() in list(self.session.projects):
                    try:
                        if self.error_label.winfo_exists():
                            self.error_label.destroy()
                    except:
                        pass
                    self.error_label = ttk.Label(self.project_id_labelframe, image=self.warning_icon,
                                                text="A Project with the same project_id already exists.\n"
                                                    "Please select an other ID.", style="Error.TLabel",
                                                compound='left')
                    self.error_label.pack(fill='x', anchor=tk.NW)
                    self.submit_btn.config(state='disabled')

                else:
                    try:
                        self.error_label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')

            else:
                self.submit_btn.config(state='disabled')
        self.project_id.trace('w', enable_submit)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        def quit(*args):
            self.project_id.set("--")
            self.master.destroy()
        self.exit_btn = ttk.Button(self.master, text="Quit", command=quit, cursor=CURSOR_HAND)
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_project,
                                        cursor=CURSOR_HAND)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

    def add_new_investigator(self, *args):
            def update_list(*args):
                if name.get() == '': 
                   messagebox.showerror("Error!","Insert the First Name!")
                   return
                if surname.get() == '':
                    messagebox.showerror("Error!","Insert the Last Name!")
                    return

                investigator = {}
                investigator['firstname'] = name.get()
                investigator['lastname'] = surname.get()
                investigator['institution'] = institution.get()
                investigator['email'] = email.get()
                try:
                    self.session.post(os.path.join(self.session.uri, '/xapi/investigators'), json=investigator)
                    self.session.clearcache()
                    self.investigators = json.loads(self.session.get(os.path.join(self.session.uri, '/xapi/investigators')).content)
                    self.investigator_list = [','.join([x['firstname'], x['lastname']]) for x in self.investigators]
                except:
                    self.investigator_list = []
                
                self.project_investigators_entry['menu'].delete(0, 'end')
                for inv in self.investigator_list:
                    self.project_investigators_entry['menu'].add_command(label=inv, command=lambda var=inv:self.project_investigator.set(var))
                investigator_popup.destroy()

            investigator_popup = tk.Toplevel()
            investigator_popup.grab_set()
            investigator_popup.title("New Investigators")
            investigator_popup.geometry("+%d+%d" % (400, 350))
            investigator_popup.resizable(False, False)
            investigator_popup.iconbitmap(PATH_IMAGE + "logo3.ico")
            name = tk.StringVar()
            name.label = ttk.Label(investigator_popup, text="First Name")
            name.label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            name.entry = ttk.Entry(investigator_popup, textvariable=name, width=20)
            name.entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            surname = tk.StringVar()
            surname.label = ttk.Label(investigator_popup, text="Last Name")
            surname.label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            surname.entry = ttk.Entry(investigator_popup, textvariable=surname, width=20)
            surname.entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            institution = tk.StringVar()
            institution.label = ttk.Label(investigator_popup, text="Institution")
            institution.label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            institution.entry = ttk.Entry(investigator_popup, textvariable=institution, width=20)
            institution.entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            email = tk.StringVar()
            email.label = ttk.Label(investigator_popup, text="Email")
            email.label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            email.entry = ttk.Entry(investigator_popup, textvariable=email, width=20)
            email.entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
            cancel_btn = ttk.Button(investigator_popup, text="Cancel", style="Secondary.TButton", cursor=CURSOR_HAND,
                                        width=10, command=lambda: investigator_popup.destroy())
            cancel_btn.grid(row=4, column=0, padx=5, pady=10, sticky=tk.W)
            submit_btn = ttk.Button(investigator_popup, text="Add", style="Secondary.TButton", cursor=CURSOR_HAND,
                                        width=10, command=update_list)
            submit_btn.grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)

    def create_new_project(self):

        def func_new_prj(*args):
            try:
                project = self.session.classes.ProjectData(
                                name=self.project_id.get(), parent=self.session)
                project.description = self.project_description_entry.get("1.0", END)
                project.keywords = ",".join(self.project_keywords_list)
                self.session.put(os.path.join(project.uri, 'accessibility', self.access_status.get()).replace('\\', '/'))
                progressbar_new_prj.stop_progress_bar()
                self.master.destroy()
                messagebox.showinfo('XNAT-PIC Uploader', 'A new project is created.')
            except exception as e:
                progressbar_new_prj.stop_progress_bar()
                self.master.destroy()
                messagebox.showerror("Error!", str(e))

        progressbar_new_prj = ProgressBar(self.master, "XNAT-PIC Uploader")
        progressbar_new_prj.start_indeterminate_bar()
        self.master.after(1000, func_new_prj)

class SubjectManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)

        self.master = tk.Toplevel()
        self.master.grab_set()
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)
        self.master.iconbitmap(PATH_IMAGE + "logo3.ico")
        
        ###########################################################################
        # Subject Widgets
        ###########################################################################
        # LabelFrame for Subject Info
        self.subject_labelframe = ttk.LabelFrame(self.master, text="Subject Info")
        self.subject_labelframe.pack(fill='x', padx=10, pady=10)

        # Parent Project
        self.parent_project = tk.StringVar()
        self.list_of_projects = list(self.session.projects)
        self.parent_project_label = ttk.Label(self.subject_labelframe, text="Parent Project *")
        self.parent_project_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_project_menu = ttk.OptionMenu(self.subject_labelframe, self.parent_project, 0, *self.list_of_projects)
        self.parent_project_menu.config(width=45)
        self.parent_project_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Subject ID
        self.subject_id = tk.StringVar()
        self.subject_id_label = ttk.Label(self.subject_labelframe, text="Subject ID *")
        self.subject_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_id_labelframe = ttk.Labelframe(self.subject_labelframe, style="Hidden.TLabelframe")
        self.subject_id_labelframe.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NW)
        self.subject_id_entry = ttk.Entry(self.subject_id_labelframe, width=50, 
                                        textvariable=self.subject_id, state='disabled')
        self.subject_id_entry.pack(fill='x', anchor=tk.NW)

        def enable_subject_id(*args):
            self.subject_id_entry.delete(0, 'end')
            self.subject_gender.set('')
            self.subject_age_entry.entry.delete(0,END)
            self.subject_age_entry.entry.insert(0, today)
            self.subject_weight_entry.delete(0,END)
            self.subject_weight_entry.insert(0,0)
            self.subject_weight.unit.set(units[0])
            self.subject_description_entry.delete(1.0,END)
            
            if self.parent_project.get() != '':
                enable_buttons([self.subject_id_entry])
            else:
                disable_buttons([self.subject_id_entry])
        self.parent_project.trace('w', enable_subject_id)

        # Subject Gender
        self.subject_gender = tk.StringVar()
        self.gender_values = ["Male", "Female", "Other"]
        self.subject_gender_label = ttk.Label(self.subject_labelframe, text="Gender")
        self.subject_gender_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_gender_menu = ttk.OptionMenu(self.subject_labelframe, self.subject_gender, 0, *self.gender_values)
        self.subject_gender_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Subject Date of Birth
        today = date.today()
        today = today.strftime("%m/%d/%Y")
        self.subject_age = tk.StringVar()
        self.subject_age.set(today)
        self.subject_age_label = ttk.Label(self.subject_labelframe, text="Date of Birth")
        self.subject_age_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_age_entry = ttk.DateEntry(self.subject_labelframe, dateformat="%m/%d/%Y")
        self.subject_age_entry.entry.config(textvariable=self.subject_age)
        self.subject_age_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        def check_date(*args):
            newdate2 = time.strptime(today, "%m/%d/%Y")
            newdate1 = time.strptime(self.subject_age.get(), "%m/%d/%Y") if self.subject_age.get() != '' else newdate2               
            if newdate1 > newdate2:
                self.subject_age.set(today)
        self.subject_age.trace('w', check_date)

        # Subject Weight
        self.subject_weight = tk.IntVar()
        self.subject_weight.unit = tk.StringVar()
        self.subject_weight_label = ttk.Label(self.subject_labelframe, text="Weight")
        self.subject_weight_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_weight_entry = ttk.Entry(self.subject_labelframe, width=50, textvariable=self.subject_weight)
        self.subject_weight_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        units = ["g", "lbs"]
        self.subject_weight_menu = ttk.OptionMenu(self.subject_labelframe, self.subject_weight.unit, units[0], *units)
        self.subject_weight_menu.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)

        # Subject Notes
        self.subject_description = tk.StringVar()
        self.subject_description_label = ttk.Label(self.subject_labelframe, text="Notes")
        self.subject_description_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        self.subject_description_entry = ttk.Text(self.subject_labelframe, width=50, height=8)
        self.subject_description_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.subject_description_scrollbar = ttk.Scrollbar(self.subject_labelframe, orient='vertical', 
                                                        command=self.subject_description_entry.yview)
        self.subject_description_scrollbar.grid(row=5, column=2, padx=0, pady=5, sticky=tk.NS)
        self.subject_description_entry.configure(yscrollcommand=self.subject_description_scrollbar.set)

        self.error = tk.StringVar()

        def enable_submit(*args):
            if self.parent_project.get() != '' and self.subject_id.get() != '':
                if self.subject_id.get() in list(self.session.projects[self.parent_project.get()].subjects.key_map.keys()):
                    if self.error.get() == '':
                        try:
                            if self.error_label.winfo_exists():
                                self.error_label.destroy()
                        except:
                            pass
                        self.error.set('Error')
                        self.error.label = ttk.Label(self.subject_id_labelframe, image=self.warning_icon,
                                                    text="A Subject with the same subject_id within "+ str(self.parent_project.get()) + 
                                                    " project\nalready exists. "
                                                    "Please select an other ID.", style="Error.TLabel",
                                                    compound='left')
                        self.error.label.pack(fill='x', anchor=tk.NW)
                        self.submit_btn.config(state='disabled')
                else:
                    try:
                        self.error.set("")
                        self.error.label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')
            else:
                try:
                    self.error.set("")
                    self.error.label.destroy()
                except:
                    pass
                self.submit_btn.config(state='disabled')
        self.subject_id.trace('w', enable_submit)
        
         #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        def quit(*args):
            self.parent_project.set("--")
            self.subject_id.set("--")
            self.master.destroy()
        self.exit_btn = ttk.Button(self.master, text="Quit", command=quit, cursor=CURSOR_HAND)
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_subject,
                                    cursor=CURSOR_HAND)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

    def create_new_subject(self):
        
        def func_new_sub(*args):
            try:
                project = self.session.projects[self.parent_project.get()]

                subject = self.session.classes.SubjectData(
                                    parent=project, label=self.subject_id.get())
                progressbar_new_sub.stop_progress_bar()
                self.master.destroy()
                messagebox.showinfo('XNAT-PIC Uploader', 'A new subject is created.') 
            except exception as e:
                progressbar_new_sub.stop_progress_bar()
                self.master.destroy()
                messagebox.showerror("Error!", str(e))
        progressbar_new_sub = ProgressBar(self.master, "XNAT-PIC Uploader")
        progressbar_new_sub.start_indeterminate_bar()
        self.master.after(1000, func_new_sub)


class ExperimentManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)

        self.master = tk.Toplevel()
        self.master.grab_set()
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)
        self.master.iconbitmap(PATH_IMAGE + "logo3.ico")

        ###########################################################################
        # Experiment Widgets
        ###########################################################################

        # LabelFrame for Experiment Info
        self.experiment_labelframe = ttk.LabelFrame(self.master, text="Experiment Info")
        self.experiment_labelframe.pack(fill='x', padx=10, pady=10)

        # Parent Project
        self.parent_project = tk.StringVar()
        self.list_of_projects = list(self.session.projects)
        self.parent_project_label = ttk.Label(self.experiment_labelframe, text="Parent Project *")
        self.parent_project_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_project_menu = ttk.OptionMenu(self.experiment_labelframe, self.parent_project, '--', *self.list_of_projects)
        self.parent_project_menu.config(width=45)
        self.parent_project_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Parent Subject
        self.parent_subject = tk.StringVar()
        if self.parent_project.get() != '--':
            self.list_of_subjects = list(self.session.projects[self.parent_project.get()].subjects.key_map.keys())
        else:
            self.list_of_subjects = []
        self.parent_subject_label = ttk.Label(self.experiment_labelframe, text="Parent Subject *")
        self.parent_subject_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_subject_menu = ttk.OptionMenu(self.experiment_labelframe, self.parent_subject, '--', *self.list_of_subjects)
        self.parent_subject_menu.config(width=45)
        self.parent_subject_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        def get_subject_list(*args):
            if self.parent_project.get() != '--' and self.parent_project.get() in self.list_of_projects:
                self.list_of_subjects = list(self.session.projects[self.parent_project.get()].subjects.key_map.keys())
            else:
                self.list_of_subjects = []
            self.parent_subject.set('--')
            self.parent_subject_menu['menu'].delete(0, 'end')
            for key in self.list_of_subjects:
                self.parent_subject_menu['menu'].add_command(label=key, command=lambda var=key:self.parent_subject.set(var))
            self.experiment_id_entry.delete(0,END)
            self.experiment_id_entry.config(state='disabled')
            self.experiment_date_entry.entry.delete(0,END)
            self.experiment_date_entry.entry.insert(0, today)
            self.experiment_description_entry.delete(1.0,END)
        self.parent_project.trace('w', get_subject_list)

        # Experiment ID
        self.experiment_id = tk.StringVar()
        self.experiment_id_label = ttk.Label(self.experiment_labelframe, text="Experiment ID *")
        self.experiment_id_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.experiment_id_labelframe = ttk.Labelframe(self.experiment_labelframe, style="Hidden.TLabelframe")
        self.experiment_id_labelframe.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NW)
        self.experiment_id_entry = ttk.Entry(self.experiment_id_labelframe, width=50, textvariable=self.experiment_id, state='disabled')
        self.experiment_id_entry.pack(fill='x', anchor=tk.NW)

        def enable_exp_id(*args):
            if self.parent_project.get() != '' and self.parent_subject.get() != '' and self.parent_subject.get() != '--':
                self.experiment_id_entry.config(state='normal')
            else:
                self.experiment_id_entry.delete(0, 'end')
                self.experiment_id_entry.config(state='disabled')
            self.experiment_date_entry.entry.delete(0,END)
            self.experiment_date_entry.entry.insert(0, today)
            self.experiment_description_entry.delete(1.0,END)
        self.parent_subject.trace('w', enable_exp_id)

        # Experiment Acquisition Date
        today = date.today()
        today = today.strftime("%m/%d/%Y")
        self.experiment_date = tk.StringVar()
        self.experiment_date.set(today)
        self.experiment_date_label = ttk.Label(self.experiment_labelframe, text="Acquisition Date")
        self.experiment_date_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.experiment_date_entry = ttk.DateEntry(self.experiment_labelframe, dateformat="%m/%d/%Y")
        self.experiment_date_entry.entry.config(textvariable=self.experiment_date)
        self.experiment_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        def check_date(*args):
            newdate2 = time.strptime(today, "%m/%d/%Y")
            newdate1 = time.strptime(self.experiment_date.get(), "%m/%d/%Y") if self.experiment_date.get() != '' else newdate2 
            if newdate1 > newdate2:
                self.experiment_date.set(today)
        self.experiment_date.trace('w', check_date)

        # Experiment Notes
        self.experiment_description = tk.StringVar()
        self.experiment_description_label = ttk.Label(self.experiment_labelframe, text="Notes")
        self.experiment_description_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        self.experiment_description_entry = ttk.Text(self.experiment_labelframe, width=50, height=8)
        self.experiment_description_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.experiment_description_scrollbar = ttk.Scrollbar(self.experiment_labelframe, orient='vertical', 
                                                        command=self.experiment_description_entry.yview)
        self.experiment_description_scrollbar.grid(row=4, column=2, padx=0, pady=5, sticky=tk.NS)
        self.experiment_description_entry.configure(yscrollcommand=self.experiment_description_scrollbar.set)

        self.error = tk.StringVar()

        def enable_submit(*args):
            if self.parent_project.get() != '' and self.parent_subject.get() != '' and self.experiment_id.get() != '':
                if self.experiment_id.get() in list(self.session.projects[self.parent_project.get()].subjects[self.parent_subject.get()].experiments.key_map.keys()):
                    if self.error.get() == "":
                        try:
                            if self.error_label.winfo_exists():
                                self.error_label.destroy()
                        except:
                            pass
                        self.error.set("Error")
                        self.error.label = ttk.Label(self.experiment_id_labelframe, image=self.warning_icon,
                                                    text="An Experiment with the same experiment_id within "+ str(self.parent_subject.get()) + 
                                                    " subject\nalready exists. Please select an other ID.", style="Error.TLabel",
                                                    compound='left')
                        self.error.label.pack(fill='x', anchor=tk.NW)
                        self.submit_btn.config(state='disabled')
                else:
                    try:
                        self.error.set("")
                        self.error.label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')
            else:
                self.submit_btn.config(state='disabled')
        self.experiment_id.trace('w', enable_submit)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        def quit(*args):
            self.parent_project.set("--")
            self.parent_subject.set("--")
            self.experiment_id.set("--")
            self.master.destroy()
        self.exit_btn = ttk.Button(self.master, text="Quit", command=quit, cursor=CURSOR_HAND)
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_experiment,
                                    cursor=CURSOR_HAND)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

    def create_new_experiment(self):
        def func_new_exp(*args):
            try:
                #################################################
                # Method to bypass the experiment object creation
                current_folder = os.path.join(os.getcwd(), "temp/Exp_1").replace("\\", "/")
                zip_dst = shutil.make_archive("temp", "zip", current_folder) # .zip file of the current subfolder

                self.session.services.import_(zip_dst,
                                            overwrite="delete", # Overwrite parameter is important!
                                            project=self.parent_project.get(),
                                            subject=self.parent_subject.get(),
                                            experiment=self.experiment_id.get(),
                                            content_type='application/zip')
                self.session.clearcache()
                experiment = self.session.projects[self.parent_project.get()].subjects[self.parent_subject.get()].experiments[self.experiment_id.get()]
                for scan in experiment.scans.listing:
                    scan.delete()
                # experiment.date = datetime.strptime(self.experiment_date.get(), "%m/%d/%Y")
                # experiment.note = self.experiment_description_entry.get("1.0", END)
                
                os.remove(zip_dst)
                
                progressbar_new_exp.stop_progress_bar()
                self.master.destroy()
                messagebox.showinfo('XNAT-PIC Uploader', 'A new experiment is created.') 
                #################################################
            except exception as e:
                progressbar_new_exp.stop_progress_bar()
                self.master.destroy()
                messagebox.showerror("Error!", str(e))


        progressbar_new_exp = ProgressBar(self.master, "XNAT-PIC Uploader")
        progressbar_new_exp.start_indeterminate_bar()
        self.master.after(1000, func_new_exp)