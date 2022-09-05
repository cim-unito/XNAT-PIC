import shutil
import tkinter as tk
from tkinter import MULTIPLE, NE, NW, SINGLE, W, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import ttkbootstrap.themes.standard 
import time
import os, re
import os.path
from functools import partial
import subprocess
import platform
from progress_bar import ProgressBar
from dicom_converter import Bruker2DicomConverter
from glob import glob
from tabulate import tabulate
import datetime 
from datetime import date
import threading
from dotenv import load_dotenv
from xnat_uploader import Dicom2XnatUploader, FileUploader
from accessory_functions import *
from idlelib.tooltip import Hovertip
from multiprocessing import Pool, cpu_count
from credential_manager import CredentialManager
import pandas
from layout_style import MyStyle
from multiprocessing import freeze_support
from ScrollableNotebook import *
from create_objects import ProjectManager, SubjectManager, ExperimentManager
from content_reader import *
from access_manager import AccessManager
from new_project_manager import NewProjectManager, NewSubjectManager, NewExperimentManager
import itertools
from Treeview import Treeview


PATH_IMAGE = "images\\"
# PATH_IMAGE = "lib\\images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
WHITE = "#ffffff"
LIGHT_GREY = "#F1FFFE"
LIGHT_GREY_DISABLED = "#91A3B1"
AZURE = "#008ad7"
AZURE_DISABLED = "#99D0EF"
DARKER_AZURE = "#006EAC"
TEXT_BTN_COLOR = "black"
TEXT_BTN_COLOR_2 = "white"
TEXT_LBL_COLOR = "black"
BG_BTN_COLOR = "#E5EAF0"
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
TITLE_FONT = ("Inkfree", 36, "italic")
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
SMALL_FONT_3 = ("Calibri", 12)
SMALL_FONT_4 = ("Calibri", 16)
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3


def check_credentials(root):
    
    dir = os.getcwd().replace('\\', '/')
    head, tail = os.path.split(dir)
    load_dotenv()
    if os.path.isfile(head + '/.env') == False or os.environ.get('secretKey') == '':
        credential_manager = CredentialManager(root)
        root.wait_window(credential_manager.popup)

class xnat_pic_gui():

    def __init__(self, root):
                   
        self.root = root
        self.root.state('zoomed') # The root widget is adapted to the screen size
        # Define the style of the root widget
        self.style_label = tk.StringVar()
        self.style_label.set('cerculean')
        style = MyStyle(self.style_label.get())
        style.configure()
        self.style = style.get_style()
        # Get the screen resolution
        if (platform.system()=='Linux'):
            cmd_show_screen_resolution = subprocess.Popen("xrandr --query | grep -oG 'primary [0-9]*x[0-9]*'",\
                                                          stdout=subprocess.PIPE, shell=True)
            screen_output =str(cmd_show_screen_resolution.communicate()).split()[1]
            self.root.screenwidth, self.root.screenheight = re.findall("[0-9]+",screen_output)
        else :
            self.root.screenwidth=self.root.winfo_screenwidth()
            self.root.screenheight=self.root.winfo_screenheight()
       
        # Adjust size based on screen resolution
        self.width = self.root.screenwidth
        self.height = self.root.screenheight
        self.my_width = self.width
        self.my_height = self.height
        self.root.geometry("%dx%d+0+0" % (self.width, self.height))
        self.root.title("   XNAT-PIC   ~   Molecular Imaging Center   ~   University of Torino   ")
        self.root.minsize(width=int(self.width/2), height=int(self.height/2)) # Set the minimum size of the working window


        # Load the images
        # Load Accept icon
        self.logo_accept = open_image(PATH_IMAGE + "Done.png", 15, 15)
        # Load Delete icon
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 15, 15)
        # Load Edit icon
        self.logo_edit = open_image(PATH_IMAGE + "Edit.png", 15, 15)
        # Load Clear icon
        self.logo_clear = open_image(PATH_IMAGE + "delete.png", 15, 15)
        # Load Search icon
        self.logo_search = open_image(PATH_IMAGE + "search_icon.png", 15, 15)
        # Load open eye
        self.open_eye = open_image(PATH_IMAGE + "open_eye.png", 15, 15)
        # Load closed eye
        self.closed_eye = open_image(PATH_IMAGE + "closed_eye.png", 15, 15)
        # Load sun icon DARK
        self.sun_icon_dark = open_image(PATH_IMAGE + "sun_icon_dark.png", 20, 20)
        # Load sun icon LIGHT
        self.sun_icon_light = open_image(PATH_IMAGE + "sun_icon_light.png", 20, 20)
        # Load home icon
        self.logo_home = open_image(PATH_IMAGE + "home.png", 15, 15)
        # Load add icon
        self.logo_add = open_image(PATH_IMAGE + "add_icon.png", 15, 15)
        # Load folder icon
        self.logo_folder = open_image(PATH_IMAGE + "folder.png", 15, 15)
        # Load save icon
        self.logo_save = open_image(PATH_IMAGE + "save.png", 15, 15)
        # Load exit icon
        self.logo_exit = open_image(PATH_IMAGE + "exit.png", 15, 15)
        # Load help icon
        self.logo_help = open_image(PATH_IMAGE + "help.png", 15, 15)
        # Load login icon
        self.logo_login = open_image(PATH_IMAGE + "login.png", 15, 15)
        # Load subdirectory icon
        self.logo_subdirectory = open_image(PATH_IMAGE + "subdirectory.png", 15, 15)
        # Load user icon
        self.user_icon = open_image(PATH_IMAGE + "user.png", 20, 20)
        # Load user icon
        self.details_icon = open_image(PATH_IMAGE + "details_icon.png", 15, 15)

        # Toolbar Menu
        def new_prj():
            project_manager = NewProjectManager(self.root)
            self.root.wait_window(project_manager.popup_prj)
        def new_sub():
            subject_manager = NewSubjectManager(self.root)
            self.root.wait_window(subject_manager.popup_sub)
        def new_exp():
            experiment_manager = NewExperimentManager(self.root)
            self.root.wait_window(experiment_manager.popup_exp)

        self.toolbar_menu = ttk.Menu(self.root)
        fileMenu = ttk.Menu(self.toolbar_menu, tearoff=0)
        new_menu = ttk.Menu(fileMenu, tearoff=0)
        new_menu.add_command(label="Project", image = self.logo_folder, compound = 'left', command=new_prj)
        new_menu.add_command(label="Subject", image = self.logo_folder, compound = 'left',command=new_sub)
        new_menu.add_command(label="Experiment", image = self.logo_folder, compound = 'left',command=new_exp)

        fileMenu.add_cascade(label="New...", image = self.logo_subdirectory, compound = 'left', menu=new_menu)
        fileMenu.add_command(label="Login", image = self.logo_login, compound = 'left')
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", image = self.logo_exit, compound = 'left', command=lambda: self.root.destroy())
        
        self.toolbar_menu.add_cascade(label="File", menu=fileMenu)
        self.toolbar_menu.add_cascade(label="Edit")
        self.toolbar_menu.add_cascade(label="Options")
        self.root.config(menu=self.toolbar_menu)

        # Logo on the top
        self.root.iconbitmap(PATH_IMAGE + "logo3.ico")

        # Initialize the Frame widget which parent is the root widgeth
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill='both', expand=1)
        self.frame_label = tk.StringVar()
        self.frame_label.set('Enter')
        
        def resize_window(*args):
            # Get the current window size
            self.width = self.root.winfo_width()
            self.height = self.root.winfo_height()
            # Load Side Logo Panel
            self.panel_img = open_image(PATH_IMAGE + "logo-panel.png", self.width/5, self.height)
            self.panel_img.label = ttk.Label(self.frame, image=self.panel_img)
            self.panel_img.label.place(x=0, y=0, anchor=tk.NW, relheight=1, relwidth=0.2)
            # Load XNAT-PIC Logo
            self.xnat_pic_logo_dark = open_image(PATH_IMAGE + "XNAT-PIC_logo.png", 2*self.width/5, self.height/3)
            self.xnat_pic_logo_light = open_image(PATH_IMAGE + "XNAT-PIC-logo-light.png", 2*self.width/5, self.height/3)
            
            if self.frame_label.get() in ["Enter", "Main"]:
                if self.style_label.get() == 'cerculean':
                    self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_dark)
                else:
                    self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_light)
                self.xnat_pic_logo_label.place(relx=0.6, rely=0.3, anchor=tk.CENTER)

            # Load Sun icon to swith to dark/light mode
            def switch_mode(*args):
                if self.style_label.get() == 'cerculean':
                    self.style_label.set('cyborg')
                    style = MyStyle('cyborg')
                    style.configure()
                    self.style = style.get_style()
                    self.dark_mode_btn.config(image=self.sun_icon_light)
                    if self.xnat_pic_logo_label.winfo_exists():
                        self.xnat_pic_logo_label.config(image=self.xnat_pic_logo_light)
                    elif self.xnat_pic_logo_label.winfo_exists() and self.frame_label.get() in ["Enter", "Main"]:
                        self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_light)
                        self.xnat_pic_logo_label.place(relx=0.3, rely=0.1, anchor=tk.NW, relheight=0.3, relwidth=0.7)
                    else:
                        pass
                    self.frame.update()
                else:
                    self.style_label.set('cerculean')
                    style = MyStyle('cerculean')
                    style.configure()
                    self.style = style.get_style()
                    self.dark_mode_btn.config(image=self.sun_icon_dark)
                    if self.xnat_pic_logo_label.winfo_exists():
                        self.xnat_pic_logo_label.config(image=self.xnat_pic_logo_dark)
                    elif self.xnat_pic_logo_label.winfo_exists() and self.frame_label.get() in ["Enter", "Main"]:
                        self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_dark)
                        self.xnat_pic_logo_label.place(relx=0.3, rely=0.1, anchor=tk.NW, relheight=0.3, relwidth=0.7)
                    else:
                        pass
                    self.frame.update()

            # Change font according to window size
            if self.width > int(2/3*self.my_width):
                self.style.configure('TButton', font = LARGE_FONT)
                self.style.configure('Title.TLabel', font = ("Inkfree", 36, "italic"))

            elif self.width > int(self.my_width/3) and self.width < int(2/3*self.my_width):
                self.style.configure('TButton', font = SMALL_FONT)
                self.style.configure('Title.TLabel', font = ("Inkfree", 30, "italic"))
            
            elif self.width < int(self.my_width/3):
                self.style.configure('TButton', font = SMALL_FONT_2)
                self.style.configure('Title.TLabel', font = ("Inkfree", 24, "italic"))
            # Update the frame widget
            self.frame.update()

        # Enter button handler method
        def enter_handler(*args):
            self.enter_btn.destroy() # Destroy the enter button and keep the Frame alive
            xnat_pic_gui.choose_your_action(self)
        # Enter button widget
        self.enter_btn = ttk.Button(self.frame, text="ENTER",
                             command=enter_handler,
                            cursor=CURSOR_HAND, bootstyle="primary")
        self.enter_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.2)
        
        # Call the resize_window method if the window size is changed by the user
        self.frame.bind("<Configure>", resize_window)

        def closed_window():
            self.root.destroy()
            self.root.quit()
        self.root.protocol("WM_DELETE_WINDOW", closed_window)
            
    # Choose to upload files, fill in the info, convert files, process images
    def choose_your_action(self):
        
        if self.toolbar_menu.winfo_exists() == 0:
            # Toolbar Menu
            def new_prj():
                project_manager = NewProjectManager(self.root)
                self.root.wait_window(project_manager.popup_prj)
            def new_sub():
                subject_manager = NewSubjectManager(self.root)
                self.root.wait_window(subject_manager.popup_sub)
            def new_exp():
                experiment_manager = NewExperimentManager(self.root)
                self.root.wait_window(experiment_manager.popup_exp)

            self.toolbar_menu = ttk.Menu(self.root)
            fileMenu = ttk.Menu(self.toolbar_menu, tearoff=0)
            new_menu = ttk.Menu(fileMenu, tearoff=0)
            new_menu.add_command(label="Project", image = self.logo_folder, compound = 'left', command=new_prj)
            new_menu.add_command(label="Subject", image = self.logo_folder, compound = 'left',command=new_sub)
            new_menu.add_command(label="Experiment", image = self.logo_folder, compound = 'left',command=new_exp)

            fileMenu.add_cascade(label="New...", image = self.logo_subdirectory, compound = 'left', menu=new_menu)
            fileMenu.add_command(label="Login", image = self.logo_login, compound = 'left')
            fileMenu.add_separator()
            fileMenu.add_command(label="Exit", image = self.logo_exit, compound = 'left', command=lambda: self.root.destroy())
            
            self.toolbar_menu.add_cascade(label="File", menu=fileMenu)
            self.toolbar_menu.add_cascade(label="Edit")
            self.toolbar_menu.add_cascade(label="Options")
            self.root.config(menu=self.toolbar_menu)


        if self.xnat_pic_logo_label.winfo_exists() == 0:
            if self.style_label.get() == 'cerculean':
                self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_dark)
            else:
                self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_light)
            self.xnat_pic_logo_label.place(relx=0.6, rely=0.3, anchor=tk.CENTER)

        self.frame_label.set("Main")
        # Action buttons           
        # Convert files Bruker2DICOM
        self.convert_btn = ttk.Button(self.frame, text="DICOM Converter",
                                    command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
        self.convert_btn.place(relx=0.6, rely=0.5, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.convert_btn,'Convert images from Bruker ParaVision format to DICOM standard')
        
        # Fill in the info
        self.info_btn = ttk.Button(self.frame, text="Project Data", 
                                    command=partial(self.metadata, self), cursor=CURSOR_HAND)
        self.info_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.info_btn,'Fill in the information about the acquisition')

        # Upload files
        def upload_callback(*args):
            self.XNATUploader(self)
        self.upload_btn = ttk.Button(self.frame, text="Uploader",
                                        command=upload_callback, cursor=CURSOR_HAND)
        self.upload_btn.place(relx=0.6, rely=0.7, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.upload_btn,'Upload DICOM images to XNAT')

        # Close button
        def close_window(*args):
            result = messagebox.askyesno("XNAT-PIC", "XNAT-PIC will be closed. Are you sure?")
            if result:
                self.root.destroy()
        self.close_btn = ttk.Button(self.frame, text="Quit", command=close_window,
                                        cursor=CURSOR_HAND)
        self.close_btn.place(relx=0.95, rely=0.9, anchor=tk.NE, relwidth=0.1)
        
    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}

            try:
                destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
            except:
                pass
            self.overall_converter(master)

        def overall_converter(self, master):
            
            # Create new frame
            master.frame_label.set("Converter")
            
            # Menu bar
            self.menu = ttk.Menu(master.root)
            file_menu = ttk.Menu(self.menu, tearoff=0)
            home_menu = ttk.Menu(self.menu, tearoff=0)
            #exit_menu = ttk.Menu(self.menu, tearoff=0)
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: exit_converter())

            file_menu.add_command(label="Clear Tree", image = master.logo_clear, compound='left', command = lambda: clear_tree())
            
            #exit_menu.add_command(label="Exit", image = master.logo_exit, compound='left', command = lambda: self.exit_metadata(master))

            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: messagebox.showinfo("XNAT-PIC","Help"))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
            #self.menu.add_cascade(label="Exit", menu=exit_menu)
            master.root.config(menu=self.menu)

            # Label Frame Main (for Title only)
            self.frame_converter = ttk.Frame(master.frame, style="Hidden.TLabelframe")
            self.frame_converter.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)
            # Frame Title
            self.frame_title = ttk.Label(self.frame_converter, text="XNAT-PIC Converter", style="Title.TLabel", anchor=tk.CENTER)
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)
            
            # Initialize variables
            self.conv_flag = tk.IntVar()
            self.folder_to_convert = tk.StringVar()
            self.converted_folder = tk.StringVar()
            self.convertion_state = tk.IntVar()

            # Convert Project
            def prj_conv_handler(*args):
                self.conv_flag.set(0)
                self.check_buttons(master, press_btn=0)
            self.prj_conv_btn = ttk.Button(self.frame_converter, text="Convert Project", 
                                            command=prj_conv_handler, cursor=CURSOR_HAND)
            self.prj_conv_btn.place(relx = 0.05, rely = 0.16, relwidth=0.22, anchor = NW)
            Hovertip(self.prj_conv_btn, "Convert a project from Bruker format to DICOM standard")

            # Convert Subject
            def sbj_conv_handler(*args):
                self.conv_flag.set(1)
                self.check_buttons(master, press_btn=1)
            self.sbj_conv_btn = ttk.Button(self.frame_converter, text="Convert Subject",
                                            command=sbj_conv_handler, cursor=CURSOR_HAND)
            self.sbj_conv_btn.place(relx = 0.5, rely = 0.16, relwidth=0.22, anchor = N)
            Hovertip(self.sbj_conv_btn, "Convert a subject from Bruker format to DICOM standard")

            # Convert Experiment
            def exp_conv_handler(*args):
                self.conv_flag.set(2)
                self.check_buttons(master, press_btn=2)
            self.exp_conv_btn = ttk.Button(self.frame_converter, text="Convert Experiment",
                                            command=exp_conv_handler, cursor=CURSOR_HAND)
            self.exp_conv_btn.place(relx = 0.95, rely = 0.16, relwidth=0.22, anchor = NE)

            Hovertip(self.exp_conv_btn, "Convert an experiment from Bruker format to DICOM standard")

            # Overwrite button
            self.overwrite_flag = tk.IntVar()
            self.btn_overwrite = ttk.Checkbutton(self.frame_converter, text="Overwrite existing folders",                               
                                onvalue=1, offvalue=0, variable=self.overwrite_flag, bootstyle="round-toggle")
            self.btn_overwrite.place(relx = 0.05, rely = 0.25, anchor = NW)
            Hovertip(self.btn_overwrite, "Overwrite already existent folders if they occur")

            # Results button
            def add_results_handler(*args):
                self.params['results_flag'] = self.results_flag.get()
            self.results_flag = tk.IntVar()
            self.btn_results = ttk.Checkbutton(self.frame_converter, text='Copy additional files', variable=self.results_flag,
                                onvalue=1, offvalue=0, command=add_results_handler, bootstyle="round-toggle")
            self.btn_results.place(relx = 0.05, rely = 0.30, anchor = NW)
            Hovertip(self.btn_results, "Copy additional files (results, parametric maps, graphs, ...)\ninto converted folders")
            
            self.separator = ttk.Separator(self.frame_converter, bootstyle="primary")
            self.separator.place(relx = 0.05, rely = 0.35, relwidth = 0.9, anchor = NW)

            # Treeview 
            def select_folder(*args):
                # Disable the buttons
                disable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])

                # Define the initial directory
                init_dir = os.path.expanduser("~").replace('\\', '/') + '/Desktop/Dataset'
                # Ask for project directory
                self.folder_to_convert.set(filedialog.askdirectory(parent=master.root, initialdir=init_dir, 
                                                                title="XNAT-PIC: Select directory in Bruker ParaVision format"))

                # Check if folder has not been selected (Cancel button)
                if self.folder_to_convert.get() == '':
                    messagebox.showerror("XNAT-PIC Converter", "Please select a folder.")
                    #enable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])
                    return

                # Check if the selected folder is related to the right convertion flag
                if self.conv_flag.get() == 0:
                    if glob(self.folder_to_convert.get() + '/**/**/**/**/**/2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related.\nPlease select an other directory.")
                        return
                elif self.conv_flag.get() == 1:
                    if glob(self.folder_to_convert.get() + '/**/**/**/**/2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related.\nPlease select an other directory.")
                        return
                elif self.conv_flag.get() == 2:
                    if glob(self.folder_to_convert.get() + '/**/**/**/2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not experiment related.\nPlease select an other directory.")
                        return
                # Reset convertion_state parameter
                self.convertion_state.set(0)
            
            def display_folder_tree(*args):

                if self.folder_to_convert.get() != '' and self.convertion_state.get() == 0:

                    dict_items = {}
                    
                    if self.tree_to_convert.tree.exists(0):
                        self.tree_to_convert.tree.delete(*self.tree_to_convert.tree.get_children())
                    j = 0
                    dict_items[str(j)] = {}
                    dict_items[str(j)]['parent'] = ""
                    dict_items[str(j)]['text'] = self.folder_to_convert.get().split('/')[-1]

                    subdir = os.listdir(self.folder_to_convert.get())
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.folder_to_convert.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.folder_to_convert.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.folder_to_convert.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            j += 1
                            # Scan directories to get subfolders
                            sub_level2 = os.listdir(os.path.join(self.folder_to_convert.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.folder_to_convert.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.folder_to_convert.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '1'
                                    dict_items[str(j)]['text'] = sub2
                                    dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.folder_to_convert.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.folder_to_convert.get(), sub, sub2))/1024/1024, 2)
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

                    self.tree_to_convert.set(dict_items)
            
            # Initialize the folder_to_upload path
            self.select_folder_button = ttk.Button(self.frame_converter, text="Select folder", style="Secondary1.TButton",
                                                    state='disabled', cursor=CURSOR_HAND, command=select_folder)
            self.select_folder_button.place(relx = 0.05, rely = 0.4, anchor = NW)

            # Clear Tree buttons
            def clear_tree(*args):
                if self.tree_to_convert.tree.exists(0):
                    self.tree_to_convert.tree.delete(*self.tree_to_convert.tree.get_children())
                if self.tree_converted.tree.exists(0):
                    self.tree_converted.tree.delete(*self.tree_converted.tree.get_children())

            self.clear_tree_btn = ttk.Button(self.frame_converter, image=master.logo_clear,
                                    cursor=CURSOR_HAND, state='disabled', command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn.place(relx = 0.37, rely = 0.72, anchor = NE)
            Hovertip(self.clear_tree_btn, "Delete tree")

            # Search entry to find objects
            def scankey(*args):
                if self.search_var.get() != '':
                    self.tree_to_convert.find_items(self.search_var.get())
                else:
                    self.tree_to_convert.remove_selection()
            
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(self.frame_converter, cursor=CURSOR_HAND, state='disabled', textvariable=self.search_var)
            self.search_entry.place(relx = 0.07, rely = 0.72, anchor = NW)
            self.search_pre_btn = ttk.Button(self.frame_converter, image=master.logo_search, state='disabled',
                                    cursor=CURSOR_HAND, command = lambda: self.search_entry.focus_set(), style="WithoutBack.TButton")
            self.search_pre_btn.place(relx = 0.05, rely = 0.72, anchor = NW)

            self.search_var.trace('w', scankey)
            
            # Details Button
            def show_folder_details_pre(*args):
            
                folder_reader = FolderDetails(self.object_folder.get())
                if glob(os.path.join(self.object_folder.get()).replace("\\", "/") + '/**/**/**/2dseq', recursive=False):
                    folder_reader.read_folder_details_raw_images()
                folder_reader.save_folder_details()
                folder_reader.show_folder_details(master.root)
                master.root.wait_window(folder_reader.popup)
                  
            def selected_object_handler(*args):
                curItem = self.tree_to_convert.tree.focus()
                parentItem = self.tree_to_convert.tree.parent(curItem)
                self.object_folder.set(os.path.join(self.folder_to_convert.get(), self.tree_to_convert.tree.item(parentItem)['text'],
                                    self.tree_to_convert.tree.item(curItem)['text']).replace("\\", "/"))
                if glob(self.object_folder.get() + '/**/**/**/2dseq', recursive=False) != []:
                    self.details_btn.config(state='normal')
                else:
                    self.details_btn.config(state='disabled')

            self.object_folder = tk.StringVar()
            self.details_btn = ttk.Button(self.frame_converter, cursor=CURSOR_HAND, image=master.details_icon, command=show_folder_details_pre,
                                            style="WithoutBack.TButton", state='disabled')
            self.details_btn.place(relx = 0.4, rely = 0.72, anchor = NE)
            Hovertip(self.details_btn, "Show details")

            # Treeview widget pre_convertion
            columns = [("#0", "Selected folder"), ("#1", "Last Update"), ("#2", "Size"), ("#3", "Type")]
            self.tree_to_convert = Treeview(self.frame_converter, columns, width=100)
            self.tree_to_convert.tree.place(relx = 0.05, rely = 0.48, relheight=0.2, relwidth=0.35, anchor = NW)
            self.tree_to_convert.scrollbar.place(relx = 0.42, rely = 0.48, relheight=0.2, anchor = NW)

            def tree_thread(*args):
                progressbar_tree = ProgressBar(master.root, "XNAT-PIC Converter")
                progressbar_tree.start_indeterminate_bar()
                if self.convertion_state.get() == 0:
                    t = threading.Thread(target=display_folder_tree, args=())
                elif self.convertion_state.get() == 1:
                    t = threading.Thread(target=display_converted_folder_tree, args=())
                t.start()
                while t.is_alive():
                    progressbar_tree.update_bar()
                progressbar_tree.stop_progress_bar()

            def display_converted_folder_tree(*args):

                if self.converted_folder.get() != '' and self.convertion_state.get() == 1:
                    dict_items = {}
                    progressbar_tree = ProgressBar(master.root, "XNAT-PIC Converter")
                    progressbar_tree.start_indeterminate_bar()
                    if self.tree_converted.tree.exists(0):
                        self.tree_converted.tree.delete(*self.tree_converted.tree.get_children())
                    head, tail = os.path.split(self.converted_folder.get())
                    j = 0
                    dict_items[str(j)] = {}
                    dict_items[str(j)]['parent'] = ""
                    dict_items[str(j)]['text'] = self.converted_folder.get().split('/')[-1]

                    subdir = os.listdir(self.converted_folder.get())
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.converted_folder.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.converted_folder.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.converted_folder.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            j += 1
                            # Scansiona le directory interne per ottenere il tree CHIUSO
                            sub_level2 = os.listdir(os.path.join(self.converted_folder.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.converted_folder.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.converted_folder.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '1'
                                    dict_items[str(j)]['text'] = sub2
                                    dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.converted_folder.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.converted_folder.get(), sub, sub2))/1024/1024, 2)
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

                    self.tree_converted.set(dict_items)

                    progressbar_tree.stop_progress_bar()
                    enable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])

            self.tree_to_convert.tree.bind("<ButtonRelease-1>", selected_object_handler)

            # Treeview post_convertion
            # Search entry to find objects
            def scankey(*args):
                if self.search_var.get() != '':
                    self.tree_converted.find_items(self.search_var.get())
                else:
                    self.tree_converted.remove_selection()

            self.search_var = tk.StringVar()
            self.search_post_entry = ttk.Entry(self.frame_converter, cursor=CURSOR_HAND, state='disabled', textvariable=self.search_var)
            self.search_post_entry.place(relx = 0.62, rely = 0.72, anchor = NW)
            self.search_post_btn = ttk.Button(self.frame_converter, image=master.logo_search, state='disabled',
                                                cursor=CURSOR_HAND, command = lambda: self.search_post_entry.focus_set(), style="WithoutBack.TButton")
            self.search_post_btn.place(relx = 0.6, rely = 0.72, anchor = NW)
            self.search_var.trace('w', scankey)

            self.clear_tree_btn_post = ttk.Button(self.frame_converter, image=master.logo_clear,
                                    cursor=CURSOR_HAND, state='normal', command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn_post.place(relx = 0.92, rely = 0.72, anchor = NE)
            Hovertip(self.clear_tree_btn_post, "Delete Tree")

            def show_folder_details_post(*args):
            
                folder_reader = FolderDetails(self.object_folder_post.get())
                if glob(os.path.join(self.object_folder_post.get()).replace("\\", "/") + '/**/**/*.dcm', recursive=False):
                    folder_reader.read_folder_details_dcm_images()
                folder_reader.save_folder_details()
                folder_reader.show_folder_details(master.root)
                master.root.wait_window(folder_reader.popup)

            # Show Details Button
            self.object_folder_post = tk.StringVar()
            self.details_btn_post = ttk.Button(self.frame_converter, cursor=CURSOR_HAND, image=master.details_icon, command=show_folder_details_post,
                                            style="WithoutBack.TButton", state='disabled')
            self.details_btn_post.place(relx = 0.95, rely = 0.72, anchor = NE)
            Hovertip(self.details_btn, "Show details")

            # Treeview widget post_convertion
            self.tree_converted = Treeview(self.frame_converter, columns, width=100)
            self.tree_converted.tree.place(relx = 0.95, rely = 0.48, relheight=0.2, relwidth=0.35, anchor = NE)
            self.tree_converted.scrollbar.place(relx = 0.58, rely = 0.48, relheight=0.2, anchor = NE)

            def selected_object_handler_post(*args):
                curItem = self.tree_converted.tree.focus()
                parentItem = self.tree_converted.tree.parent(curItem)
                self.object_folder_post.set(os.path.join(self.converted_folder.get(), self.tree_converted.tree.item(parentItem)['text'],
                                    self.tree_converted.tree.item(curItem)['text']).replace("\\", "/"))
                if glob(self.object_folder_post.get().replace("\\", "/") + '/**/**/*.dcm', recursive=False) != []:
                    self.details_btn_post.config(state='normal')
                else:
                    self.details_btn_post.config(state='disabled')

            self.convertion_state.trace('w', tree_thread)
            self.tree_converted.tree.bind("<ButtonRelease-1>", selected_object_handler_post)

            # EXIT Button 
            def exit_converter():
                result = messagebox.askquestion("XNAT-PIC Converter", "Do you want to exit?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, Checkbutton, ...)
                    destroy_widgets([self.frame_converter, self.menu])
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_text = tk.StringVar()
            self.exit_btn = ttk.Button(self.frame_converter, cursor=CURSOR_HAND,
                                    textvariable=self.exit_text,  style="Secondary1.TButton", command=exit_converter)
            self.exit_text.set('Exit')
            self.exit_btn.place(relx = 0.05, rely = 0.9, relwidth=0.15, anchor = NW)

            # NEXT Button
            def next_btn_handler(*args):
                if self.conv_flag.get() == 0:
                    self.converted_folder.set(self.folder_to_convert.get() + '_dcm')
                    disable_buttons([self.exit_btn, self.next_btn])
                    self.prj_convertion(master)
     
                elif self.conv_flag.get() == 1:
                    conv_folder = str(os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-1])  + '_dcm', 
                                                self.folder_to_convert.get().split('/')[-1]))
                    self.converted_folder.set(conv_folder.replace("\\",'/'))
                    disable_buttons([self.exit_btn, self.next_btn])
                    self.sbj_convertion(master)
    
                elif self.conv_flag.get() == 2:
                    self.converted_folder.set(os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-2])  + '_dcm', 
                                                '/'.join(self.folder_to_convert.get().split('/')[-2:])))
                    disable_buttons([self.exit_btn, self.next_btn])
                    self.exp_convertion(master)
                       
                else:
                    self.converted_folder.set('')

            self.next_btn = ttk.Button(self.frame_converter, text="Next", cursor=CURSOR_HAND,  style="Secondary1.TButton", command=next_btn_handler,
                                    state='disabled')
            self.next_btn.place(relx = 0.95, rely = 0.9, relwidth=0.15, anchor = NE)

        def check_buttons(self, master, press_btn=0):

            def back():
                destroy_widgets([self.frame_converter])
                self.overall_converter(master)

            # Initialize the press button value
            self.press_btn = press_btn

            # Change the EXIT button into BACK button and modify the command associated with it
            self.exit_text.set("Back")
            self.exit_btn.configure(command=back)

            # if press_btn == 0:
            # Disable main buttons
            disable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])
            enable_buttons([self.select_folder_button, self.search_entry, self.search_pre_btn, self.clear_tree_btn, self.search_post_entry, self.search_post_btn])

            # View what conversion you are doing (Project, Subject, Experiment)
            if self.conv_flag.get() == 0:
                working_text = 'Convert Project'
            elif self.conv_flag.get() == 1:
                working_text = 'Convert Subject'
            elif self.conv_flag.get() == 2:
                working_text = 'Convert Experiment'

            self.working_label = ttk.Label(self.frame_converter, text = working_text, font = SMALL_FONT)
            self.working_label.place(relx = 0.5, rely = 0.35, anchor = CENTER)

            # Enable NEXT button only if all the requested fields are filled
            def enable_next(*args):
                if self.folder_to_convert.get() != '':
                    enable_buttons([self.next_btn])
                else:
                    disable_buttons([self.next_btn])
            self.folder_to_convert.trace('w', enable_next)
            
        def prj_convertion(self, master):

            # Check for the chosen directory
            if not self.folder_to_convert.get():
                messagebox.showerror("XNAT-PIC Converter", "The selected folder does not exists. Please select an other one.")
                return

            if glob(self.folder_to_convert.get() + '/**/**/**/**/**/2dseq', recursive=False) == []:
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related")
                return
            
            master.root.deiconify()
            master.root.update()
            # Define the project destination folder
            # self.prj_dst = self.folder_to_convert.get() + '_dcm'
            self.prj_dst = self.converted_folder.get()

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def prj_converter():

                # Get the list of the subject into the project
                list_sub = os.listdir(self.folder_to_convert.get())
                # Clear list_sub from configuration files (e.g. desktop.ini)
                list_sub = [sub for sub in list_sub if sub.endswith('.ini')==False]
                # Initialize the list of conversion errors
                self.conversion_err = []
                # Loop over subjects
                for j, dir in enumerate(list_sub, 0):
                    # Show the current step on the progress bar
                    progressbar.show_step(j + 1, len(list_sub))
                    
                    # Define the current subject path 
                    current_folder = os.path.join(self.folder_to_convert.get(), dir).replace('\\', '/')

                    if os.path.isdir(current_folder):
                        current_dst = os.path.join(self.prj_dst, dir).replace('\\', '/')
                        # Check if the current subject folder already exists
                        if os.path.isdir(current_dst):
                            # Case 1 --> The directory already exists
                            if self.overwrite_flag.get() == 1:
                                # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                                shutil.rmtree(current_dst)
                                os.makedirs(current_dst)
                            else:
                                # Existent folder without overwriting flag set to 0 --> ignore folder
                                self.conversion_err.append(current_folder.split('/')[-1])
                                continue
                        else:
                            # Case 2 --> The directory does not exist
                            if current_dst.split('/')[-1].count('_dcm') >= 1:
                                # Check to avoid already converted folders
                                self.conversion_err.append(current_folder.split('/')[-1])
                                continue
                            else:
                                # Create the new destination folder
                                os.makedirs(current_dst)

                        # Set progress bar caption to the current scan folder
                        progressbar.set_caption('Converting ' + str(current_folder.split('/')[-1]) + ' ...')

                        # Get the list of the experiments into the subject
                        list_exp = os.listdir(current_folder)
                        # Clear list_exp from configuration files (e.g. desktop.ini)
                        list_exp = [exp for exp in list_exp if exp.endswith('.ini')==False]

                        for k, exp in enumerate(list_exp):
                            print('Converting ' + str(exp))
                            exp_folder = os.path.join(current_folder, exp).replace('\\', '/')
                            exp_dst = os.path.join(current_dst, exp).replace('\\','/')
                            list_scans = self.converter.get_list_of_folders(exp_folder, exp_dst)

                            # Start the multiprocessing conversion: one pool per each scan folder
                            with Pool(processes=int(cpu_count() - 1)) as pool:
                                pool.map(self.converter.convert, list_scans)

                    # Update the current step of the progress bar
                    progressbar.update_progressbar(j + 1, len(list_sub))
                    # Set progress bar caption 'done' to the current folder
                    progressbar.set_caption('Converting ' + str(current_folder.split('/')[-1]) + ' ...done!')
            
            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Project Converter')
            progressbar.start_determinate_bar()

            # Perform DICOM convertion through separate thread (different from the main thread)
            tp = threading.Thread(target=prj_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                progressbar.update_bar(0)
            else:
                progressbar.stop_progress_bar()
            
            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","The conversion of the project is done!\n\n\n\n"
                                "Exceptions:\n\n" +
                                str([str(x) for x in self.conversion_err])[1:-1])

            self.convertion_state.set(1)
            enable_buttons([self.exit_btn])   
                
        def sbj_convertion(self, master):

            # Check for chosen directory
            if not self.folder_to_convert.get():
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.folder_to_convert.get() + '/**/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related")
                return

            master.root.deiconify()
            master.root.update()
            # head, tail = os.path.split(self.folder_to_convert.get())
            # head = head + '_dcm'
            # project_foldername = tail.split('.',1)[0]
            # self.sub_dst = os.path.join(head, project_foldername).replace('\\', '/')
            self.sub_dst = self.converted_folder.get()

            # Start converter
            self.converter = Bruker2DicomConverter(self.params)

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.sub_dst):
                # Case 1 --> The directory already exists
                if self.overwrite_flag.get() == 1:
                    # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                    shutil.rmtree(self.sub_dst)
                    os.makedirs(self.sub_dst)
                else:
                    # Existent folder without overwriting flag set to 0 --> ignore folder
                    messagebox.showerror("XNAT-PIC Converter", "Destination folder %s already exists" % self.sub_dst)
                    self.converted_folder.set(self.sub_dst)
                    return
            else:
                # Case 2 --> The directory does not exist
                if self.sub_dst.split('/')[-1].count('_dcm') >= 1:
                    # Check to avoid already converted folders
                    messagebox.showerror("XNAT-PIC Converter", "Chosen folder %s already converted" % self.sub_dst)
                    self.converted_folder.set(os.path.join(self.folder_to_convert.get().split('/')[:-2], self.sub_dst))
                    return
                else:
                    # Create the new destination folder
                    os.makedirs(self.sub_dst)

            def sbj_converter():

                list_exp = os.listdir(self.folder_to_convert.get())
                list_exp = [exp for exp in list_exp if exp.endswith('.ini') == False]
                for k, exp in enumerate(list_exp):
                    print('Converting ' + str(exp))
                    progressbar.show_step(k + 1, len(list_exp))
                    progressbar.update_progressbar(k, len(list_exp))
                    exp_folder = os.path.join(self.folder_to_convert.get(), exp).replace('\\','/')
                    exp_dst = os.path.join(self.sub_dst, exp).replace('\\','/')

                    list_scans = self.converter.get_list_of_folders(exp_folder, exp_dst)
        
                    progressbar.set_caption('Converting ' + str(exp_folder.split('/')[-1]) + ' ...')
                    with Pool(processes=int(cpu_count() - 1)) as pool:
                        pool.map(self.converter.convert, list_scans)
                    progressbar.set_caption('Converting ' + str(exp_folder.split('/')[-1]) + ' ...done!')

            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Subject Converter')
            progressbar.start_determinate_bar()

            # Initialize and start convertion thread
            tp = threading.Thread(target=sbj_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                # As long as the thread is working, update the progress bar
                progressbar.update_bar(0.0001)
            progressbar.stop_progress_bar()

            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","Done! Your subject is successfully converted.")
            self.convertion_state.set(1)
            enable_buttons([self.exit_btn]) 

        def exp_convertion(self, master):

            # Check for chosen directory
            if not self.folder_to_convert.get():
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.folder_to_convert.get() + '/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not experiment related")
                return

            master.root.deiconify()
            master.root.update()
            # head, tail = os.path.split(self.folder_to_convert.get())
            # head2, tail2 = os.path.split(head)
            # head2 = head2 + '_dcm'
            # self.exp_dst = os.path.join(head2, tail2, tail).replace('\\', '/')
            self.exp_dst = self.converted_folder.get()

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def exp_converter():
                list_scans = self.converter.get_list_of_folders(self.folder_to_convert.get(), self.exp_dst)
    
                progressbar.set_caption('Converting ' + str(self.folder_to_convert.get().split('/')[-1]) + ' ...')
                with Pool(processes=int(cpu_count() - 1)) as pool:
                    pool.map(self.converter.convert, list_scans)
                progressbar.set_caption('Converting ' + str(self.folder_to_convert.get().split('/')[-1]) + ' ...done!')

            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Experiment Converter')
            progressbar.start_indeterminate_bar()

            # Initialize and start convertion thread
            tp = threading.Thread(target=exp_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                # As long as the thread is working, update the progress bar
                progressbar.update_bar()
            progressbar.stop_progress_bar()

            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","Done! Your experiment is successfully converted.")
            self.convertion_state.set(1)
            enable_buttons([self.exit_btn])
                 
    # Fill in information
    class metadata():

        def __init__(self, master):

            # Disable all buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
        
            # Popup
            self.popup_metadata = ttk.Toplevel()
            self.popup_metadata.title("XNAT-PIC ~ Project Data")
            #self.popup_metadata.geometry("+%d+%d" % (0.5, 0.5))
            master.root.eval(f'tk::PlaceWindow {str(self.popup_metadata)} center')
            self.popup_metadata.resizable(False, False)
            self.popup_metadata.grab_set()
            
            # If you want the logo 
            self.popup_metadata.iconbitmap(PATH_IMAGE + "logo3.ico")

            # Browse: select if it is a project, subject or experiment
            self.popup_metadata_frame = ttk.LabelFrame(self.popup_metadata, text="Select directory", style="Popup.TLabelframe")
            self.popup_metadata_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

            # Project     
            self.popup_metadata.dir = tk.StringVar()
            self.popup_metadata.project = ttk.Radiobutton(self.popup_metadata_frame, text="Project", variable = self.popup_metadata.dir, 
                                                           value = "Project", style="Popup.TRadiobutton")   
            self.popup_metadata.project.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
            # Subject      
            self.popup_metadata.subject = ttk.Radiobutton(self.popup_metadata_frame, text="Subject", variable = self.popup_metadata.dir, 
                                                           value = "Subject", style="Popup.TRadiobutton")   
            self.popup_metadata.subject.grid(row=1, column=0, padx=10, pady=10, sticky=tk.N)
            # Experiment      
            self.popup_metadata.experiment = ttk.Radiobutton(self.popup_metadata_frame, text="Experiment", variable = self.popup_metadata.dir, 
                                                           value = "Experiment", style="Popup.TRadiobutton")   
            self.popup_metadata.experiment.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
            
            self.popup_metadata.dir.set("Project") 
            
            self.popup_metadata.entry_browse = ttk.Entry(self.popup_metadata_frame, state='disabled', takefocus = 0, width= 80)
            self.popup_metadata.entry_browse.grid(row=2, column=0, padx=10, pady=5, sticky=tk.N)

            self.popup_metadata.button_browse = ttk.Button(self.popup_metadata_frame, text='Browse', command = lambda: self.select_folder(master), style="MainPopup.TButton")
            self.popup_metadata.button_browse.grid(row=3, column=0, padx=10, pady=5, sticky=tk.N)

            self.popup_metadata.button_ok = ttk.Button(self.popup_metadata, image = master.logo_accept,
                                                command = lambda: self.layout_metadata(master) , cursor=CURSOR_HAND)
            self.popup_metadata.button_ok.grid(row=2, column=1, padx=10, pady=5, sticky=NW)

            # If the popup is closed, it re-enables the buttons
            def enable():
                self.popup_metadata.destroy()

                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
                
            self.popup_metadata.button_cancel = ttk.Button(self.popup_metadata, image = master.logo_delete,
                                                command = enable, cursor=CURSOR_HAND)
            self.popup_metadata.button_cancel.grid(row=2, column=0, padx=10, pady=5, sticky=NE)

            self.popup_metadata.protocol('WM_DELETE_WINDOW', enable)       
        
        def select_folder(self, master): 
            
            disable_buttons([self.popup_metadata.button_browse, self.popup_metadata.button_cancel, self.popup_metadata.button_ok])

            # Choose your directory (button and menu)
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select " + str(self.popup_metadata.dir.get()) + " directory!")
            
            # Write the path in the entry
            self.popup_metadata.entry_browse['state'] = tk.NORMAL
            self.popup_metadata.entry_browse.delete(0, tk.END)
            self.popup_metadata.entry_browse.insert(0, str(self.information_folder))
            self.popup_metadata.entry_browse['state'] = tk.DISABLED
            
            enable_buttons([self.popup_metadata.button_browse, self.popup_metadata.button_cancel, self.popup_metadata.button_ok])
            # If there is no folder selected, re-enable the buttons and return
            if not self.information_folder:
                self.popup_metadata.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
                return
            
            master.frame_label.set("Project Data")         

        def layout_metadata(self, master): 
            
            if not self.popup_metadata.entry_browse.get():
                messagebox.showerror('XNAT-PIC','Select a folder!')
                return

            self.popup_metadata.destroy()

            try:
                self.frame_metadata.destroy()
            except:
                pass
            
            # Read the data
            if str(self.popup_metadata.dir.get()) == "Project":
                self.project_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 0)
                self.selection = 'Selected Project: ' + self.project_name
            elif str(self.popup_metadata.dir.get()) == "Subject":
                self.subject_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 1)
                self.selection = 'Selected Subject: ' + self.subject_name
            elif str(self.popup_metadata.dir.get()) == "Experiment":
                self.experiment_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 2)
                self.selection = 'Selected Experiment: ' + self.experiment_name
            self.results_dict = params[0]
            self.todos = params[1]
            self.path_list = params[2]
            self.path_list1 = params[3]

            #################### Update the frame ####################
            destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
            self.frame_metadata = ttk.Frame(master.frame)
            self.frame_metadata.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)
            # Frame Title
            self.frame_title = ttk.Label(self.frame_metadata, text="XNAT-PIC Project Data", style='Title.TLabel')
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)
            #################### Menu ###########################
            def browse_fun():
                #disable_buttons([self.browse_btn, self.modify_btn, self.confirm_btn, self.multiple_confirm_btn]) 
                self.__init__(master)

            self.menu = ttk.Menu(master.root)
            file_menu = ttk.Menu(self.menu, tearoff=0)
            home_menu = ttk.Menu(self.menu, tearoff=0)
            #exit_menu = ttk.Menu(self.menu, tearoff=0)
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: self.home_metadata(master))

            file_menu.add_command(label="Select Folder", image = master.logo_folder, compound='left', command = browse_fun)
            file_menu.add_separator()
            file_menu.add_command(label ="Show details",  image=master.details_icon, compound='left', command= lambda: self.show_folder_details(master),)
            file_menu.add_command(label="Add ID", image = master.logo_add, compound='left',command = lambda: self.add_ID(master))
            file_menu.add_command(label="Add Custom Variables", image = master.logo_add, compound='left', command = lambda: self.add_custom_variable(master))
            file_menu.add_command(label="Clear Custom Variables", image = master.logo_clear, compound='left', command = lambda: self.clear_metadata())
            file_menu.add_separator()
            file_menu.add_command(label="Save All", image = master.logo_save, compound='left', command = lambda: self.save_metadata())
            file_menu.add_separator()
            file_menu.add_command(label="Save New Project", image = master.logo_save, compound='left', command = lambda: self.save_new_project(master))
            
            #exit_menu.add_command(label="Exit", image = master.logo_exit, compound='left', command = lambda: self.exit_metadata(master))

            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: messagebox.showinfo("XNAT-PIC","Help"))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
            #self.menu.add_cascade(label="Exit", menu=exit_menu)
            master.root.config(menu=self.menu)

            #################### Folder list #################### 
            ### Selected folder label
            self.name_selected = ttk.Label(self.frame_metadata, text=self.selection, style = "UnderTitle.TLabel")
            self.name_selected.place(relx = 0.5, rely = 0.13, anchor = CENTER)
            # ### Tab Notebook
            self.notebook = ScrollableNotebook(self.frame_metadata, wheelscroll=True, tabmenu=True)
            self.notebook.place(relx = 0.2, rely = 0.35, relheight=0.25, relwidth=0.25, anchor = tk.CENTER)
            
            # Sorts the tabs first by length and then alphabetically
            frame_notebook = []
            self.listbox_notebook = []
            for key in sorted(self.todos, key=len):
                frame_notebook.append(tk.Frame(self.notebook))
                frame_notebook[-1].pack()
                self.notebook.add(frame_notebook[-1], text=key, underline=0, sticky=tk.NE + tk.SW)
                self.listbox_notebook.append(tk.Listbox(frame_notebook[-1], selectbackground = AZURE, relief=tk.FLAT, font=SMALL_FONT_3, selectmode=SINGLE, takefocus = 0))
                self.listbox_notebook[-1].insert(tk.END, *self.todos[key])
                self.listbox_notebook[-1].pack(side=LEFT, fill = BOTH, expand = 1, padx = 5, pady=5)
                
                # Yscrollbar for listbox
                self.my_yscrollbar = ttk.Scrollbar(self.listbox_notebook[-1], orient="vertical")
                self.listbox_notebook[-1].config(yscrollcommand = self.my_yscrollbar.set)
                self.my_yscrollbar.config(command = self.listbox_notebook[-1].yview)
                self.my_yscrollbar.pack(side="right", fill="y")

                # Xscrollbar for listbox
                self.my_xscrollbar = ttk.Scrollbar(self.listbox_notebook[-1], orient="horizontal")
                self.listbox_notebook[-1].config(xscrollcommand = self.my_xscrollbar.set)
                self.my_xscrollbar.config(command = self.listbox_notebook[-1].xview)
                self.my_xscrollbar.pack(side="bottom", fill="x")

            self.notebook.enable_traversal()
           
            #################### Subject form ####################
            # ID
            # Label frame for ID: folder selected, project, subject, exp and acq. date
            self.label_frame_ID = ttk.LabelFrame(self.frame_metadata, text="ID", padding=5, bootstyle="primary")
            #
            # Scroll bar in the Label frame ID
            self.canvas_ID = tk.Canvas(self.label_frame_ID)
            self.frame_ID = tk.Frame(self.canvas_ID)

            self.vsb_ID = ttk.Scrollbar(self.label_frame_ID, orient="vertical", command=self.canvas_ID.yview)
            self.canvas_ID.configure(yscrollcommand=self.vsb_ID.set)  

            self.hsb_ID = ttk.Scrollbar(self.label_frame_ID, orient="horizontal", command=self.canvas_ID.xview)
            self.canvas_ID.configure(xscrollcommand=self.hsb_ID.set)     

            self.vsb_ID.pack(side="right", fill="y")
            self.hsb_ID.pack(side="bottom", fill="x")

            self.canvas_ID.pack(side = LEFT, fill = BOTH, expand = 1)
            self.canvas_ID.create_window((0,0), window=self.frame_ID, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_ID.bind("<Configure>", lambda event, canvas=self.canvas_ID: OnFrameConfigure(canvas))
            self.label_frame_ID.place(relx = 0.4, rely = 0.22, relheight=0.25, relwidth=0.43, anchor = tk.NW)
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            keys_ID = ["Folder", "Project", "Subject", "Experiment", "Acquisition_date"]
            # Entry ID 
            self.entries_variable_ID = []  
            self.entries_value_ID = []          
            count = 0
            for key in keys_ID:
                # Variable
                self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
                self.entries_variable_ID[-1].insert(0, key)
                self.entries_variable_ID[-1]['state'] = 'disabled'
                self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width= 20 if key == "Acquisition_date" else 44))
                self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            # Calendar for acq. date
            self.datevar = tk.StringVar()
            self.cal = ttk.DateEntry(self.frame_ID, dateformat = '%Y-%m-%d')
            self.cal.entry.config(textvariable=self.datevar)         
            self.cal.entry.configure(width=10)
            self.cal.entry['state'] = 'normal'
            self.cal.entry.delete(0, tk.END)
            self.cal.entry['state'] = 'disabled'
            self.cal.button['state'] = 'disabled'
            self.cal.grid(row=4, column=1, padx = 5, pady = 5, sticky=E)

            #####################################################################
            # Custom Variables (CV)
            self.label_frame_CV = ttk.LabelFrame(self.frame_metadata, text="Custom Variables", padding = 5, bootstyle="primary")
            
            # Scroll bar in the Label frame CV
            self.canvas_CV = tk.Canvas(self.label_frame_CV)
            self.frame_CV = tk.Frame(self.canvas_CV)

            self.vsb_CV = ttk.Scrollbar(self.label_frame_CV, orient="vertical", command=self.canvas_CV.yview)
            self.canvas_CV.configure(yscrollcommand=self.vsb_CV.set)  
            self.hsb_CV = ttk.Scrollbar(self.label_frame_CV, orient="horizontal", command=self.canvas_CV.xview)
            self.canvas_CV.configure(xscrollcommand=self.hsb_CV.set)     

            self.vsb_CV.pack(side="right", fill="y")     
            self.hsb_CV.pack(side="bottom", fill="x")
            self.canvas_CV.pack(side = LEFT, fill = BOTH, expand = 1)
            self.canvas_CV.create_window((0,0), window=self.frame_CV, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_CV.bind("<Configure>", lambda event, canvas=self.canvas_CV: OnFrameConfigure(canvas))
            self.label_frame_CV.place(relx = 0.40, rely = 0.53, relheight=0.16, relwidth=0.43, anchor = tk.NW)
            
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            keys_CV = ["Group", "Timepoint", "Dose"]
            # Entry CV  
            self.entries_variable_CV = []  
            self.entries_value_CV = []          
            count = 0
            for key in keys_CV:
                # Variable
                self.entries_variable_CV.append(ttk.Entry(self.frame_CV, takefocus = 0, width=15))
                self.entries_variable_CV[-1].insert(0, key)
                self.entries_variable_CV[-1]['state'] = 'disabled'
                self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                # Value
                self.entries_value_CV.append(ttk.Entry(self.frame_CV, state='disabled', takefocus = 0, width=25))
                self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1
            

            # Dose: the dose entry has a StringVar because the unit of measure will be automatically added to the entered value
            self.dosevar = tk.StringVar()
            self.entries_value_CV[2].config(textvariable=self.dosevar)

            # Group Menu
            OPTIONS = ["untreated", "treated"]
            self.selected_group = tk.StringVar()
            self.group_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_group, width=10)
            self.group_menu['values'] = OPTIONS
            self.group_menu['state'] = 'disabled'
            self.group_menu.grid(row=0, column=2, padx = 5, pady = 5, sticky=W)
            
            # Timepoint
            self.OPTIONS = ["pre", "post"]
            self.selected_timepoint = tk.StringVar()
            self.timepoint_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_timepoint, width=10)
            self.timepoint_menu['values'] = self.OPTIONS
            self.timepoint_menu['state'] = 'disabled'
            self.timepoint_menu.grid(row=1, column=2, padx = 5, pady = 5, sticky=W)
            
            self.time_entry_value = tk.StringVar()
            self.time_entry = ttk.Entry(self.frame_CV, state='disabled', takefocus = 0, width=5, textvariable=self.time_entry_value)
            self.time_entry.grid(row=1, column=3, padx = 5, pady = 5, sticky=W)

            self.OPTIONS1 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
            self.selected_timepoint1 = tk.StringVar()
            self.timepoint_menu1 = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_timepoint1, width=7)
            self.timepoint_menu1['values'] = self.OPTIONS1
            self.timepoint_menu1['state'] = 'disabled'
            self.timepoint_menu1.grid(row=1, column=4, padx = 5, pady = 5, sticky=W)

            # Dose
            OPTIONS2 = ["mg/kg"]
            self.selected_dose = tk.StringVar()
            self.dose_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_dose, width=10)
            self.dose_menu['values'] = OPTIONS2
            self.dose_menu['state'] = 'disabled'
            self.dose_menu.grid(row=2, column=2, padx = 5, pady = 5, sticky=W)
            
            #################### Browse the metadata ####################
            self.browse_btn = ttk.Button(self.frame_metadata, text="Browse", command = browse_fun, cursor=CURSOR_HAND, takefocus = 0, style = "Secondary.TButton")
            self.browse_btn.place(relx=0.20, rely=0.55, anchor=tk.CENTER, relwidth=0.15)

            #################### Modify the metadata ####################
            self.modify_btn = ttk.Button(self.frame_metadata, text="Modify", command = lambda: self.modify_metadata(), cursor=CURSOR_HAND, takefocus = 0, style = "Secondary1.TButton")
            self.modify_btn.place(relx=0.20, rely=0.8, anchor=tk.CENTER, relwidth=0.2)

            #################### Confirm the metadata ####################
            self.confirm_btn = ttk.Button(self.frame_metadata, text="Confirm", command = lambda: self.confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0, style = "Secondary1.TButton")
            self.confirm_btn.place(relx=0.50, rely=0.8, anchor=tk.CENTER, relwidth=0.2)

            #################### Confirm multiple metadata ####################
            self.multiple_confirm_btn = ttk.Button(self.frame_metadata, text="Multiple Confirm", command = lambda: self.confirm_multiple_metadata(master), cursor=CURSOR_HAND, takefocus = 0, style = "Secondary1.TButton")
            self.multiple_confirm_btn.place(relx=0.80, rely=0.8, anchor=tk.CENTER, relwidth=0.2)

            self.load_info(master)

        #################### Load the info about the selected subject ####################
        def load_info(self, master):
            # Find the initial tab
            self.index_tab = self.notebook.notebookTab.index("current")
            self.tab_name = self.notebook.notebookTab.tab(self.index_tab, "text")
            self.my_listbox = self.listbox_notebook[self.index_tab]
            self.selected_index = None
            self.selected_folder = None

            def items_selected(event):
                # Clear all the combobox and the entry
                self.selected_group.set('')
                self.selected_timepoint.set('')
                self.selected_timepoint1.set('')
                self.time_entry.delete(0, tk.END)
                self.selected_dose.set('')
                self.cal.entry['state'] = 'disabled'
                self.cal.button['state'] = 'disabled'

                disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu])
                
                # Find the tab
                self.index_tab = self.notebook.notebookTab.index("current")
                self.tab_name =  self.notebook.notebookTab.tab(self.index_tab, "text")
                self.my_listbox = self.listbox_notebook[self.index_tab]

                # Get selected index in the listbox
                self.selected_index = self.my_listbox.curselection()[0]
                self.selected_folder = self.tab_name + '#' + self.my_listbox.get(self.selected_index)

                tmp_dict = self.results_dict[self.selected_folder]

                # Split the dictionary into ID and CV
                complete_list = [list(group) for key, group in itertools.groupby(tmp_dict, lambda x: x == 'C_V') if not key]
                dict_ID = {'Folder' : self.selected_folder}
                dict_ID.update({k: v for k, v in tmp_dict.items() if k in complete_list[0]})
                dict_CV =  {k: v for k, v in tmp_dict.items() if k in complete_list[1]}
                
                #################################################################
                # Updates the ID frame based on the selected variables and values
                diff_ID = len(self.entries_variable_ID) - len(dict_ID) 
                
                # If the number of entries is greater than the number of variables, eliminate the excess entries
                if diff_ID > 0:
                    for i in range(len(dict_ID), len(self.entries_variable_ID)):
                        self.entries_variable_ID[i].destroy()
                        self.entries_value_ID[i].destroy()
                    del self.entries_variable_ID[len(dict_ID) : len(self.entries_variable_ID)]
                    del self.entries_value_ID[len(dict_ID) : len(self.entries_value_ID)]
                # If the number of entries is less than the number of variables, insert the entries
                elif diff_ID < 0:
                    for j in range(len(self.entries_variable_ID), len(dict_ID)):
                        self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
                        self.entries_variable_ID[-1].grid(row=j, column=0, padx = 5, pady = 5, sticky=W)
                        self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width = 44))
                        self.entries_value_ID[-1].grid(row=j, column=1, padx = 5, pady = 5, sticky=W)
                
                # Modify the values ​​of the entries with the values ​​of the selected experiment
                ind = 0
                for key, value in dict_ID.items():
                    # Variable ID
                    self.entries_variable_ID[ind]['state'] = 'normal'
                    self.entries_variable_ID[ind].delete(0, tk.END)
                    self.entries_variable_ID[ind].insert(0, key)
                    self.entries_variable_ID[ind]['state'] = 'disabled'
                    # Value ID
                    self.entries_value_ID[ind]['state'] = 'normal'
                    self.entries_value_ID[ind].delete(0, tk.END)
                    self.entries_value_ID[ind].insert(0, value if value is not None else '')
                    self.entries_value_ID[ind]['state'] = 'disabled'
                    ind += 1
                
                current_date = self.entries_value_ID[4].get()
                self.cal.entry['state'] = 'normal'
                self.cal.entry.delete(0, tk.END)
                self.cal.entry.insert(0, current_date)
                self.cal.entry['state'] = 'disabled'

                #################################################################
                # Updates the CV frame based on the selected variables and values
                diff_CV = len(self.entries_variable_CV) - len(dict_CV) 
                
                # If the number of entries is greater than the number of variables, eliminate the excess entries
                if diff_CV > 0:
                    for i in range(len(dict_CV), len(self.entries_variable_CV)):
                        self.entries_variable_CV[i].destroy() 
                        self.entries_value_CV[i].destroy() 
                    del self.entries_variable_CV[len(dict_CV) : len(self.entries_variable_CV)]
                    del self.entries_value_CV[len(dict_CV) : len(self.entries_value_CV)]
                # If the number of entries is less than the number of variables, insert the entries
                elif diff_CV < 0:
                    for j in range(len(self.entries_variable_CV), len(dict_CV)):
                        self.entries_variable_CV.append(ttk.Entry(self.frame_CV, takefocus = 0, width=15))
                        self.entries_variable_CV[-1].grid(row=j, column=0, padx = 5, pady = 5, sticky=W)
                        self.entries_value_CV.append(ttk.Entry(self.frame_CV, state='disabled', takefocus = 0, width = 25))
                        self.entries_value_CV[-1].grid(row=j, column=1, padx = 5, pady = 5, sticky=W)
                
                # Modify the values ​​of the entries with the values ​​of the selected experiment
                ind = 0
                for key, value in dict_CV.items():
                    # Variable ID
                    self.entries_variable_CV[ind]['state'] = 'normal'
                    self.entries_variable_CV[ind].delete(0, tk.END)
                    self.entries_variable_CV[ind].insert(0, key)
                    self.entries_variable_CV[ind]['state'] = 'disabled'
                    # Value ID
                    self.entries_value_CV[ind]['state'] = 'normal'
                    self.entries_value_CV[ind].delete(0, tk.END)
                    self.entries_value_CV[ind].insert(0, value if value is not None else '')
                    self.entries_value_CV[ind]['state'] = 'disabled'
                    ind += 1

            # Add the event to the list of listbox (press Tab)   
            for i in range(len(self.listbox_notebook)):
                self.listbox_notebook[i].bind('<Tab>', items_selected)
            
        # Details Button
        def show_folder_details(self, master):
            if self.selected_folder is None:
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return 
            substring = self.path_list1.get(self.selected_folder)
            folder_reader = FolderDetails(substring)
            if glob(os.path.join(substring).replace("\\", "/") + '/**/**/**/2dseq', recursive=False):
                    folder_reader.read_folder_details_raw_images()
            elif glob(os.path.join(substring).replace("\\", "/") + '/**/**/*.dcm', recursive=False):
                    folder_reader.read_folder_details_dcm_images()
            folder_reader.save_folder_details()
            folder_reader.show_folder_details(master.root)
            master.root.wait_window(folder_reader.popup)


        def modify_metadata(self):
            # Check before editing the data
            if self.selected_folder is None:
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return 

            # Normal entry ID
            for i in range(1, len(self.entries_value_ID)):
                self.entries_value_ID[i]['state'] = 'normal'
            
            # The acquisition data field remains locked. Only one value can be entered from the entry.
            self.entries_value_ID[4]['state'] = 'disabled'
            
            # Normal entry CV
            for i in range(0, len(self.entries_value_CV)):
                self.entries_value_CV[i]['state'] = 'normal'
            
            # The timepoint field remains locked. Only one value can be entered from the entry.
            self.entries_value_CV[1]['state'] = 'disabled'

            self.cal.entry['state'] = 'normal'
            self.cal.button['state'] = 'normal'

            # # Acquisition date: you can modify date with the calendar           
            def date_entry_selected(*args):
                self.entries_value_ID[4]['state'] = tk.NORMAL
                self.entries_value_ID[4].delete(0, tk.END)
                self.entries_value_ID[4].insert(0, str(self.cal.entry.get()))
                if self.entries_value_ID[4].get():
                    try:
                        acq_date = datetime.datetime.strptime(self.entries_value_ID[4].get(), '%Y-%m-%d')
                        self.today = date.today()
                        self.today = self.today.strftime('%Y-%m-%d')
                        if acq_date.strftime('%Y-%m-%d') > self.today:
                            self.entries_value_ID[4].delete(0, tk.END)
                            raise Exception("The date entered is greater than today's date")
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", str(e))
                        self.entries_value_ID[4].delete(0, tk.END)
                        self.entries_value_ID[4]['state'] = tk.DISABLED
                        raise

                self.entries_value_ID[4]['state'] = tk.DISABLED
                self.my_listbox.selection_set(self.selected_index)
            
            self.datevar.trace('w', date_entry_selected)


            # Option menu for the group (treated/untreated)
            self.group_menu['state'] = 'readonly'
            def group_changed(event):
                """ handle the group changed event """
                self.entries_value_CV[0].delete(0, tk.END)
                self.entries_value_CV[0].insert(0, str(self.selected_group.get()))                    
                self.my_listbox.selection_set(self.selected_index)

            self.group_menu.bind("<<ComboboxSelected>>", group_changed)

            # Add the unit of measure to the number entered for the dose
            self.dose_menu['state'] = 'readonly'
            def dose_changed(event):
                """ handle the dose changed event """
                value_dose = ''
                if self.entries_value_CV[2].get():
                    try:
                        dose = str(self.entries_value_CV[2].get())
                        value_dose = dose.replace(' mg/kg','')
                        float(value_dose)
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", 'Insert a number in dose')
                        raise

                self.entries_value_CV[2].delete(0, tk.END)
                self.entries_value_CV[2].insert(0, str(value_dose) + ' ' + str(self.selected_dose.get()))                    
                self.my_listbox.selection_set(self.selected_index)

            self.dose_menu.bind("<<ComboboxSelected>>", dose_changed)
            
            # Option menu for the timepoint
            self.timepoint_menu1['state'] = 'readonly'
            self.time_entry['state'] = 'normal'
            self.timepoint_menu['state'] = 'readonly'

            def timepoint_changed(*args):
                self.entries_value_CV[1].config(state=tk.NORMAL)
                """ handle the timepoint changed event """
                if str(self.time_entry.get()) or str(self.selected_timepoint1.get()):
                    timepoint_str = str(self.selected_timepoint.get()) + "-" + str(self.time_entry.get()) + "-" + str(self.selected_timepoint1.get())
                else:
                    timepoint_str = str(self.selected_timepoint.get()) 

                self.my_listbox.selection_set(self.selected_index)

                if self.time_entry.get():
                    try:
                        float(self.time_entry.get())
                    except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Insert a number in the timepoint entry")

                self.entries_value_CV[1].delete(0, tk.END)
                self.entries_value_CV[1].insert(0, timepoint_str)
                self.entries_value_CV[1].config(state=tk.DISABLED)

            self.timepoint_menu.bind("<<ComboboxSelected>>", timepoint_changed)
            self.time_entry.bind('<Return>', timepoint_changed)
            self.time_entry.bind('<FocusOut>', timepoint_changed)
            #self.time_entry_value.trace('w', timepoint_changed)
            self.timepoint_menu1.bind("<<ComboboxSelected>>", timepoint_changed)

        def check_entries(self):

            if not self.entries_value_ID[1].get():
                raise Exception ("Insert the name of the project!")

            if not self.entries_value_ID[2].get():
                raise Exception ("Insert the name of the subject!")

            if self.entries_value_ID[4].get():
                try:
                    datetime.datetime.strptime(self.entries_value_ID[4].get(), '%Y-%m-%d')
                except Exception as e:
                    raise Exception ("Incorrect data format in acquisition date, should be YYYY-MM-DD")

            if self.entries_value_CV[1].get() and '-' in  self.entries_value_CV[1].get(): 
                if not str(self.entries_value_CV[1].get()).split('-')[0] in self.OPTIONS:
                    raise Exception ("Select pre/post in timepoint!")
                if not str(self.entries_value_CV[1].get()).split('-')[2] in self.OPTIONS1:
                    raise Exception ("Select seconds, minutes, hours, days, weeks, months, years in timepoint")

                input_num = str(self.entries_value_CV[1].get()).split('-')[1]
                try:
                    float(input_num)
                except Exception as e: 
                    raise Exception ("Insert a number in timepoint between pre/post and seconds, minutes, hours..")  

            if  self.entries_value_CV[2].get():
                try:
                    # Check if the entry is a number
                    dose_value = self.entries_value_CV[2].get().replace(' mg/kg',"")
                    float(dose_value)
                except Exception as e: 
                    raise Exception ("Insert a number in dose")

        # Update the values and save the values in a txt file        
        def save_entries(self, my_key, multiple):
            
            if multiple == 0:
            # Single confirm
                array_ID = range(1, len(self.entries_variable_ID))
                array_CV = range(0, len(self.entries_variable_CV))
            elif multiple ==1:
            # Multple confirm
                array_ID = self.list_ID
                array_CV = self.list_CV
                
            tmp_ID = {}
            # Update the info in the txt file ID
            for i in array_ID:
                tmp_ID.update({self.entries_variable_ID[i].get() : self.entries_value_ID[i].get()})     
                self.entries_variable_ID[i]['state'] = tk.DISABLED
                self.entries_value_ID[i]['state'] = tk.DISABLED 
            
            tmp_ID.update({"C_V" : ""}) 
            
            # self.entries_value_ID[1]['state'] = tk.NORMAL
            # Update the info in the txt file CV
            for i in array_CV:
                tmp_ID.update({self.entries_variable_CV[i].get() : self.entries_value_CV[i].get()})     
                self.entries_variable_CV[i]['state'] = tk.DISABLED
                self.entries_value_CV[i]['state'] = tk.DISABLED 

            self.results_dict[my_key].update(tmp_ID)
           
            # Clear all 
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            self.selected_dose.set('')
            disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu, self.cal])
            # Saves the changes made by the user in the txt file
            substring = self.path_list1.get(my_key)
            name_txt = str(my_key).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
            tmp_path = substring + "\\" + name_txt
            try:
                with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                    meta_file.write(tabulate(self.results_dict[my_key].items(), headers=['Variable', 'Value']))
            except Exception as e: 
                    messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
                    raise    
        def confirm_metadata(self):
            # Check if a folder is selected         
            if self.selected_folder is None:
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return

            try:
                self.check_entries()
            except Exception as e: 
                messagebox.showerror("XNAT-PIC", "Error in checking fields: " + str(e))  
                raise

            try:
                self.save_entries(self.selected_folder, multiple=0)
            except Exception as e: 
                messagebox.showerror("XNAT-PIC", "Error in saving: " + str(e))  
                raise

        # #################### Confirm multiple metadata ####################
        def confirm_multiple_metadata(self, master):

            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
            
            # Disable entry
            for i in range(len(self.entries_variable_ID)): 
                self.entries_variable_ID[i]['state'] = tk.DISABLED
                self.entries_value_ID[i]['state'] = tk.DISABLED 

            for i in range(len(self.entries_variable_CV)):  
                self.entries_variable_CV[i]['state'] = tk.DISABLED
                self.entries_value_CV[i]['state'] = tk.DISABLED    

            # Clear all 
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            self.selected_dose.set('')
            self.cal.entry['state'] = tk.DISABLED
            self.cal.button['state'] = tk.DISABLED


            # Check if a folder is selected         
            if self.selected_folder is None:
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                return

            messagebox.showinfo("Project Data","Select the ID fields you want to copy.")
            #self.my_listbox.selection_set(self.selected_index)

            # Select the fields that you want to copy
            self.list_ID = []
            # Confirm ID
            def multiple_confirm_ID(row):
                self.list_ID.append(row)
                btn_multiple_confirm_ID[row].destroy()
                btn_multiple_delete_ID[row].destroy()
                count_list.pop()
                # If the user has finished all the selections of the ID, he moves on to the selection of CV
                if len(count_list) == 1:
                    self.select_CV(master)

            # Delete ID
            def multiple_delete_ID(row):
                btn_multiple_confirm_ID[row].destroy()
                btn_multiple_delete_ID[row].destroy()
                count_list.pop()
                # If the user has finished all the selections of the ID, he moves on to the selection of CV
                if len(count_list) == 1:
                    self.select_CV(master)

            btn_multiple_confirm_ID = []
            btn_multiple_delete_ID = []
            count_list = []
            for i in range(0, len(self.entries_variable_ID)):
                btn_multiple_confirm_ID.append(ttk.Button(self.frame_ID, image = master.logo_accept, 
                                                command=lambda row=i: multiple_confirm_ID(row), cursor=CURSOR_HAND))
                btn_multiple_confirm_ID[-1].grid(row=i, column=2, padx = 5, pady = 5, sticky=NW)
                btn_multiple_confirm_ID[0].destroy()
                btn_multiple_delete_ID.append(ttk.Button(self.frame_ID, image = master.logo_delete, 
                                                command=lambda row=i: multiple_delete_ID(row), cursor=CURSOR_HAND))
                btn_multiple_delete_ID[-1].grid(row=i, column=3, padx = 5, pady = 5, sticky=NW)
                btn_multiple_delete_ID[0].destroy()
                count_list = btn_multiple_confirm_ID.copy()
            
        def select_CV(self, master):
            messagebox.showinfo("Project Data","Select the Custom Variables you want to copy.")
            #self.my_listbox.selection_set(self.selected_index)
            # Select the fields that you want to copy
            self.list_CV = []
            # Confirm ID
            def multiple_confirm_CV(row):
                self.list_CV.append(row)
                btn_multiple_confirm_CV[row].destroy()
                btn_multiple_delete_CV[row].destroy()
                count_list.pop()
                # If the user has finished all the selections of the CV, he moves on to the selection of experiments
                if len(count_list) == 0:
                    self.select_exp(master)

            # Delete ID
            def multiple_delete_CV(row):
                btn_multiple_confirm_CV[row].destroy()
                btn_multiple_delete_CV[row].destroy()
                count_list.pop()
                # If the user has finished all the selections of the CV, he moves on to the selection of experiments
                if len(count_list) == 0:
                    self.select_exp(master)

            btn_multiple_confirm_CV = []
            btn_multiple_delete_CV = []
            count_list = []
            for i in range(0, len(self.entries_variable_CV)):
                btn_multiple_confirm_CV.append(ttk.Button(self.frame_CV, image = master.logo_accept, 
                                                command=lambda row=i: multiple_confirm_CV(row), cursor=CURSOR_HAND))
                btn_multiple_confirm_CV[-1].grid(row=i, column=5, padx = 5, pady = 5, sticky=NW)
                btn_multiple_delete_CV.append(ttk.Button(self.frame_CV, image = master.logo_delete, 
                                                command=lambda row=i: multiple_delete_CV(row), cursor=CURSOR_HAND))
                btn_multiple_delete_CV[-1].grid(row=i, column=6, padx = 5, pady = 5, sticky=NW)
                count_list = btn_multiple_confirm_CV.copy()
            
        def select_exp(self, master):
            messagebox.showinfo("Metadata","Select the folders from the box on the left for which to copy the info and then press confirm or cancel!")
            #enable_buttons([self.my_listbox])
            #tab_names = [self.notebook.tab(i, state='normal') for i in self.notebook.tabs()]
            self.my_listbox.selection_set(self.selected_index) 
            for i in range(len(self.listbox_notebook)):
                self.listbox_notebook[i]['selectmode'] = MULTIPLE
                self.listbox_notebook[i]['exportselection']=False   

            # The user presses confirm 
            def items_selected2():
                self.no_btn.destroy()
                self.ok_btn.destroy()
                #self.list_tab_listbox.append(self.seltext)
                result = messagebox.askquestion("Multiple Confirm", "Are you sure you want to save data for the selected folders?\n", icon='warning')
                seltext = []
                self.list_tab_listbox = []

                if result == 'yes':
                    # Read all the selected item
                    for i in self.notebook.notebookTab.tabs():
                        index_tab = self.notebook.notebookTab.index(i)
                        tab_name = self.notebook.notebookTab.tab(i, "text")
                        seltext = [tab_name + '#' + self.listbox_notebook[int(index_tab)].get(index) 
                                        for index in self.listbox_notebook[int(index_tab)].curselection()]
                        if seltext:
                            self.list_tab_listbox.append(seltext)

                    try:
                        self.check_entries()
                    except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Error in checking fields" + str(e))  
                        raise
                
                for x in range(len(self.list_tab_listbox)):
                    for y in range(len(self.list_tab_listbox[x])):
                        try:
                            self.save_entries(self.list_tab_listbox[x][y], multiple=1)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Error in saving" + str(e))  
                            raise
                
                # Clear all 
                self.selected_group.set('')
                self.selected_dose.set('')
                self.selected_timepoint.set('')
                self.selected_timepoint1.set('')
                self.time_entry.delete(0, tk.END)
                self.cal.entry.delete(0, tk.END)
                disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.cal.entry, self.cal.button])
                # Clear the focus and the select mode of the listbox is single
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                self.my_listbox.selection_clear(0, 'end')
                for i in range(len(self.listbox_notebook)):
                    self.listbox_notebook[i]['selectmode'] = SINGLE 
                    self.listbox_notebook[i]['exportselection']= TRUE  
                self.load_info(master)

            self.ok_btn = ttk.Button(self.frame_metadata, image = master.logo_accept, command = items_selected2, cursor=CURSOR_HAND)
            self.ok_btn.place(relx = 0.16, rely = 0.48, anchor = NW)
            
            # The user presses cancel
            def items_cancel():
                self.no_btn.destroy()
                self.ok_btn.destroy()
                # Clear the focus and the select mode of the listbox is single
                messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                for i in range(len(self.listbox_notebook)):
                    self.listbox_notebook[i]['selectmode'] = SINGLE 
                    self.listbox_notebook[i]['exportselection']= TRUE 
            self.no_btn = ttk.Button(self.frame_metadata, image = master.logo_delete, command = items_cancel, cursor=CURSOR_HAND)
            self.no_btn.place(relx = 0.24, rely = 0.48, anchor = NE)
                
        # #################### Add ID #################
        def add_ID(self, master):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # Disable btns
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
            # I use len(all_entries) to get nuber of next free row
            next_row = len(self.entries_variable_ID)
            
            # Add entry variable ID
            ent_variable = ttk.Entry(self.frame_ID, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_ID.append(ent_variable)                 

            # Add entry value ID in second col
            ent_value = ttk.Entry(self.frame_ID, takefocus = 0, width=44)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_ID.append(ent_value)

            # Confirm
            def confirm_ID(next_row):
                pos = list(self.results_dict[self.selected_folder].keys()).index('C_V')
                items = list(self.results_dict[self.selected_folder].items())
                if self.entries_variable_ID[next_row].get():
                    if self.entries_value_ID[next_row].get():
                        value_ID = self.entries_value_ID[next_row].get()
                    else:
                        value_ID = ''
                    items.insert(pos, (self.entries_variable_ID[next_row].get(), value_ID))
                    self.results_dict[self.selected_folder] = dict(items)
                    state = self.entries_value_ID[1]['state']
                    self.entries_variable_ID[next_row]['state'] = tk.DISABLED
                    self.entries_value_ID[next_row]['state'] = state
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                    btn_confirm_ID.destroy()
                    btn_reject_ID.destroy()
                else:
                    messagebox.showerror("XNAT-PIC", "Insert ID")
                 
            btn_confirm_ID = ttk.Button(self.frame_ID, image = master.logo_accept, 
                                            command=lambda: confirm_ID(next_row), cursor=CURSOR_HAND)
            btn_confirm_ID.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=NW)

            # Delete
            def reject_ID(next_row):
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                self.entries_variable_ID[next_row].destroy()
                self.entries_value_ID[next_row].destroy()
                btn_confirm_ID.destroy()
                btn_reject_ID.destroy()
            btn_reject_ID = ttk.Button(self.frame_ID, image = master.logo_delete,  
                                            command=lambda: reject_ID(next_row), cursor=CURSOR_HAND)
            btn_reject_ID.grid(row=next_row, column=3, padx = 5, pady = 5, sticky=NW)


        # #################### Add Custom Variable #################
        def add_custom_variable(self, master):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # Disable btns
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
            # I get number of next free row
            next_row = len(self.entries_variable_CV)
            
            # Add entry variable CV
            ent_variable = ttk.Entry(self.frame_CV, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_CV.append(ent_variable)                 

            # Add entry value in second col
            ent_value = ttk.Entry(self.frame_CV, takefocus = 0, width=25)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_CV.append(ent_value)
            
            # Confirm
            def confirm_CV(next_row):
                if self.entries_variable_CV[next_row].get():
                    if self.entries_value_CV[next_row].get():
                        value_CV = self.entries_value_CV[next_row].get()
                    else:
                        value_CV = ''
                    tmp_CV = {self.entries_variable_CV[next_row].get() : value_CV}
                    self.results_dict[self.selected_folder].update(tmp_CV) 
                    state = self.entries_value_ID[1]['state']    
                    self.entries_variable_CV[next_row]['state'] = tk.DISABLED
                    self.entries_value_CV[next_row]['state'] = state
                    enable_buttons([self.modify_btn, self.confirm_btn, self.browse_btn, self.multiple_confirm_btn, self.browse_btn])
                    btn_confirm_CV.destroy()
                    btn_reject_CV.destroy()
                else:
                    messagebox.showerror("XNAT-PIC", "Insert Custom Variable")
                     
            btn_confirm_CV = ttk.Button(self.frame_CV, image = master.logo_accept, 
                                            command=lambda: confirm_CV(next_row), cursor=CURSOR_HAND)
            btn_confirm_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NW)

            # Delete
            def reject_CV(next_row):
                self.entries_variable_CV[next_row].destroy()
                self.entries_value_CV[next_row].destroy()
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.browse_btn])
                btn_confirm_CV.destroy()
                btn_reject_CV.destroy()
            btn_reject_CV = ttk.Button(self.frame_CV, image = master.logo_delete, 
                                            command=lambda: reject_CV(next_row), cursor=CURSOR_HAND)
            btn_reject_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NE)

        ##################### Clear the metadata ####################              
        def clear_metadata(self):
            # Clear all the combobox and the entry
            self.selected_dose.set('')
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.cal.entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)

            state = self.entries_value_ID[1]['state']
            # Set empty string in all the entries
            for i in range(0, len(self.entries_variable_CV)):
                    self.entries_value_CV[i]['state'] = tk.NORMAL
                    self.entries_value_CV[i].delete(0, tk.END)
                    self.entries_value_CV[i]['state'] = state

        def save_new_project(self, master):
            # Save the new project based on the information entered by the user
            new_prj_path = filedialog.askdirectory(parent=self.frame_metadata, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select the folder where to save the new project!")
            
            if not new_prj_path:
                return
            
            def func_save_prj():
                for key, value in self.results_dict.items():
                    new_exp_path = new_prj_path + '\\' + value.get('Project') + '\\' + value.get('Subject') + '\\' + value.get('Experiment')
                    progressbar.set_caption('Creating: ' + new_exp_path.replace('\\', '/'))

                    # The path already exists
                    if os.path.exists(new_exp_path.replace('\\', '/')):
                        answer = messagebox.askyesno('XNAT-PIC', 'The experiment ' + new_exp_path.replace('\\', '/') + ' already exists. Overwrite it?')

                        if answer is True:
                            try:
                                shutil.rmtree((new_exp_path).replace('//', os.sep))
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC", str(e))
                                raise
                        else:
                            continue
                    
                    # Save the experiment
                    try:
                        shutil.copytree(self.path_list1.get(key), new_exp_path.replace('\\', '/'))
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", str(e))
                        continue
            
            # Start the progress bar
            progressbar = ProgressBar(self.frame_metadata, bar_title='XNAT-PIC New Project')
            progressbar.start_indeterminate_bar()
            
            # Disable button
            disable_buttons([self.browse_btn,self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
            try:
                # Save the project through separate thread (different from the main thread)
                tp = threading.Thread(target=func_save_prj, args=())
                tp.start()
                while tp.is_alive() == True:
                    # As long as the thread is working, update the progress bar
                    progressbar.update_bar()
                progressbar.stop_progress_bar()
                enable_buttons([self.browse_btn,self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                messagebox.showinfo("XNAT-PIC", 'The new project was created!')
            except Exception as e:
                enable_buttons([self.browse_btn,self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                
        # #################### Save all the metadata ####################
        def save_metadata(self):
            tmp_global_path = str(self.information_folder) + "\\" + self.project_name + '_' + 'Custom_Variables.xlsx'
            try:
                df = pandas.DataFrame.from_dict(self.results_dict, orient='index')
                writer = pandas.ExcelWriter(tmp_global_path.replace('\\', '/'), engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                messagebox.showinfo("XNAT-PIC", "File saved successfully")
            except Exception as e: 
                    messagebox.showerror("XNAT-PIC", "Save failed: " + str(e))  
                    raise
            
        # #################### Exit the metadata ####################
        def exit_metadata(self, master):
            result = messagebox.askquestion("Exit", "Do you want to exit?", icon='warning')
            if result == 'yes':
                destroy_widgets([self.frame_metadata, self.menu])
                master.root.after(1500, xnat_pic_gui.choose_your_action(master))

        ##################### Home ####################
        def home_metadata(self, master):
                destroy_widgets([self.frame_metadata, self.menu])
                master.root.after(2000, xnat_pic_gui.choose_your_action(master))
    
    class XNATUploader():

        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            access_manager = AccessManager(master.root)
            master.root.wait_window(access_manager.popup)

            if access_manager.connected == False:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            else:
                destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
                self.session = access_manager.session
                self.overall_uploader(master)

        def overall_uploader(self, master):
                           
            #################### Create the new frame ####################
            master.frame_label.set("Uploader")
            #############################################
            ################ Main Buttons ###############

            self.frame_uploader = ttk.Frame(master.frame, style="Hidden.TLabelframe")
            self.frame_uploader.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)

            # Menu
            self.menu = ttk.Menu(master.root)
            file_menu = ttk.Menu(self.menu, tearoff=0)
            home_menu = ttk.Menu(self.menu, tearoff=0)
            #exit_menu = ttk.Menu(self.menu, tearoff=0)
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: exit_uploader())

            file_menu.add_command(label="Clear Tree", image = master.logo_clear, compound='left', command = lambda: clear_tree())
            
            #exit_menu.add_command(label="Exit", image = master.logo_exit, compound='left', command = lambda: self.exit_metadata(master))

            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: messagebox.showinfo("XNAT-PIC","Help"))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
            #self.menu.add_cascade(label="Exit", menu=exit_menu)
            master.root.config(menu=self.menu)


            # Frame Title
            self.frame_title = ttk.Label(self.frame_uploader, text="XNAT-PIC Uploader", style="Title.TLabel", anchor=tk.CENTER)
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)

            # User Icon
            self.user_btn = ttk.Menubutton(self.frame_uploader, text=self.session.logged_in_user, image=master.user_icon, compound='right',
                                                cursor=CURSOR_HAND)
            self.user_btn.menu = Menu(self.user_btn, tearoff=0)
            self.user_btn["menu"] = self.user_btn.menu
            self.user_btn.menu.add_command(label="Exit", command=lambda: exit_uploader())
            self.user_btn.place(relx = 0.95, rely = 0.05, anchor = E)

            # Initialize variables
            self.upload_type = tk.IntVar()

            # Upload project
            def project_handler(*args):
                self.upload_type.set(0)
                # self.uploader_data.config(text="Project Uploader")
                self.check_buttons(master, press_btn=0)
            self.prj_btn = ttk.Button(self.frame_uploader, text="Project",
                                    command=project_handler, cursor=CURSOR_HAND)
            Hovertip(self.prj_btn, "Upload Project")
            self.prj_btn.place(relx = 0.05, rely = 0.12, relwidth = 0.18, anchor = NW)
            
            # Upload subject
            def subject_handler(*args):
                self.upload_type.set(1)
                # self.uploader_data.config(text="Subject Uploader")
                self.check_buttons(master, press_btn=1)
            self.sub_btn = ttk.Button(self.frame_uploader, text="Subject",
                                    command=subject_handler, cursor=CURSOR_HAND)
            Hovertip(self.sub_btn, "Upload Subject")
            self.sub_btn.place(relx = 0.29, rely = 0.12, relwidth = 0.18, anchor = NW)

            # Upload experiment
            def experiment_handler(*args):
                self.upload_type.set(2)
                # self.uploader_data.config(text="Experiment Uploader")
                self.check_buttons(master, press_btn=2)
            self.exp_btn = ttk.Button(self.frame_uploader, text="Experiment", 
                                    command=experiment_handler, cursor=CURSOR_HAND)
            Hovertip(self.exp_btn, "Upload Experiment")
            self.exp_btn.place(relx = 0.71, rely = 0.12, relwidth = 0.18, anchor = NE)
            
            # Upload file
            def file_handler(*args):
                self.upload_type.set(3)
                # self.uploader_data.config(text="File Uploader")
                self.check_buttons(master, press_btn=3)
            self.file_btn = ttk.Button(self.frame_uploader, text="File",
                                    command=file_handler, cursor=CURSOR_HAND)
            Hovertip(self.file_btn, "Upload File")
            self.file_btn.place(relx = 0.95, rely = 0.12, relwidth = 0.18, anchor = NE)
            
            self.separator1 = ttk.Separator(self.frame_uploader, bootstyle="primary")
            self.separator1.place(relx = 0.05, rely = 0.21, relwidth = 0.9, anchor = NW)

            # Define a string variable in order to check the current selected item of the Treeview widget
            self.selected_item_path = tk.StringVar()
            
            def select_folder(*args):
                # Disable the buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                # Define the initial directory
                init_dir = os.path.expanduser("~").replace('\\', '/') + '/Desktop/Dataset'
                # Ask the user to insert the desired directory
                self.folder_to_upload.set(filedialog.askdirectory(parent=master.frame, initialdir=init_dir, 
                                                        title="XNAT-PIC Uploader: Select directory in DICOM format to upload"))
                if self.folder_to_upload.get() == '':
                    messagebox.showerror("XNAT-PIC Converter", "Please select a folder.")
                    return
                # Reset and clear the selected_item_path defined from Treeview widget selection
                self.selected_item_path.set('')

            def folder_selected_handler(*args):
                if self.folder_to_upload.get() != '':

                    dict_items = {}

                    # Check for pre-existent tree
                    if self.tree.tree.exists(0):
                        # # Check for the name of the previous tree
                        # if self.tree.item(0)['text'] != self.folder_to_upload.get().split('/')[-1]:
                        # If the folder name is changed, then delete the previous tree
                        self.tree.tree.delete(*self.tree.tree.get_children())

                    # Define the main folder into the Treeview object
                    j = 0
                    dict_items[str(j)] = {}
                    dict_items[str(j)]['parent'] = ""
                    dict_items[str(j)]['text'] = self.folder_to_upload.get().split('/')[-1]
                    # Scan the folder to get its tree
                    subdir = os.listdir(self.folder_to_upload.get())
                    # Check for OS configuration files and remove them
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.folder_to_upload.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.folder_to_upload.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            # Add the item like a file
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.folder_to_upload.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = '0'
                            dict_items[str(j)]['text'] = sub
                            j += 1
                            # Scansiona le directory interne per ottenere il tree CHIUSO
                            sub_level2 = os.listdir(os.path.join(self.folder_to_upload.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.folder_to_upload.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.folder_to_upload.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '1'
                                    dict_items[str(j)]['text'] = sub2
                                    dict_items[str(j)]['values'] = (edit_time, str(file_weight) + "KB", "File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.folder_to_upload.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.folder_to_upload.get(), sub, sub2))/1024/1024, 2)
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
                    self.search_entry.config(state='normal')
                    self.search_label.config(state='normal')
                    self.tree.set(dict_items)
            
            # Initialize the folder_to_upload path
            self.folder_to_upload = tk.StringVar()
            self.select_folder_button = ttk.Button(self.frame_uploader, text="Select folder", style="Secondary.TButton",
                                                    state='disabled', cursor=CURSOR_HAND, command=select_folder)
            self.select_folder_button.place(relx = 0.05, rely = 0.25, relwidth = 0.18, anchor = NW)

            # Treeview for folder visualization
            def get_selected_item(*args):
                selected_item = self.tree.tree.selection()[0]
                
                if self.folder_to_upload.get().split('/')[-1] == self.tree.tree.item(selected_item, "text"):
                    self.selected_item_path.set(self.folder_to_upload.get())
                else:
                    parent_item = self.tree.tree.parent(selected_item)
                    if self.folder_to_upload.get().split('/')[-1] == self.tree.tree.item(parent_item, "text"):
                        self.selected_item_path.set('/'.join([self.folder_to_upload.get(), 
                                self.tree.tree.item(selected_item, "text")]))
                    else:
                        higher_parent_item = self.tree.tree.parent(parent_item)
                        if self.folder_to_upload.get().split('/')[-1] == self.tree.tree.item(higher_parent_item, "text"):
                            self.selected_item_path.set('/'.join([self.folder_to_upload.get(), self.tree.tree.item(parent_item, "text"),
                                self.tree.tree.item(selected_item, "text")]))
            
            columns = [("#0", "Selected folder"), ("#1", "Last Update"), ("#2", "Size"), ("#3", "Type")]
            self.tree = Treeview(self.frame_uploader, columns, width=80)
            self.tree.tree.place(relx = 0.05, rely = 0.31, relheight=0.30, relwidth=0.4, anchor = NW)
            self.tree.scrollbar.place(relx = 0.47, rely = 0.31, relheight=0.30, anchor = NE)
            self.tree.tree.bind("<ButtonRelease-1>", get_selected_item)

            def load_tree(*args):
                progressbar_tree = ProgressBar(master.root, "XNAT-PIC Uploader")
                progressbar_tree.start_indeterminate_bar()
                t = threading.Thread(target=folder_selected_handler, args=())
                t.start()
                while t.is_alive() == True:
                    progressbar_tree.update_bar()
                progressbar_tree.stop_progress_bar()

            self.folder_to_upload.trace('w', load_tree)

            # Clear Tree buttons
            def clear_tree(*args):
                if self.tree.tree.exists(0):
                    self.tree.tree.delete(*self.tree.tree.get_children())
                    self.search_entry.config(state='disabled')
                    self.search_label.config(state='disabled')
                    self.folder_to_upload.set("")

            self.clear_tree_btn = ttk.Button(self.frame_uploader, image=master.logo_clear,
                                    cursor=CURSOR_HAND, command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn.place(relx = 0.47, rely = 0.25, anchor = NE)

            # Search Bar
            def scankey(*args):
                if self.search_var.get() != "":
                    self.tree.find_items(self.search_var.get())
                else:
                    self.tree.remove_selection()
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(self.frame_uploader, cursor=CURSOR_HAND, textvariable=self.search_var,
                                             state='disabled')
            #self.search_entry.place(relx = 0.15, rely = 0.65, relwidth=0.1, anchor = NW)
            self.search_label = ttk.Button(self.frame_uploader, image=master.logo_search, command = lambda: self.search_entry.focus_set(), state='disabled', cursor=CURSOR_HAND)
            # self.search_label.place(relx = 0.05, rely = 0.65, anchor = NW)

            # self.search_var.trace('w', scankey)

            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = ttk.Checkbutton(self.frame_uploader, variable=self.add_file_flag, onvalue=1, offvalue=0, 
                                text="Additional Files", state='disabled', bootstyle="round-toggle", cursor=CURSOR_HAND)
            self.add_file_btn.place(relx = 0.29, rely = 0.25, anchor = NW)
            
            # Label Frame Uploader Custom Variables
            self.custom_var_labelframe = ttk.Labelframe(self.frame_uploader, text = 'Custom Variables')
            self.custom_var_labelframe.place(relx = 0.53, rely = 0.31, relheight=0.30, relwidth = 0.42, anchor = NW)
            
            # Custom Variables
            self.n_custom_var = tk.IntVar()
            self.n_custom_var.set(3)
            custom_var_options = list(range(0, 4))
            self.custom_var_list = ttk.OptionMenu(self.custom_var_labelframe, self.n_custom_var, 0, *custom_var_options)
            self.custom_var_list.config(width=2, cursor=CURSOR_HAND)
            self.custom_var_list.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
            self.custom_var_label = ttk.Label(self.custom_var_labelframe, text="Custom Variables")
            self.custom_var_label.grid(row=0, column=1, padx=2, pady=5, sticky=tk.NW)

            # Show Custom Variables
            def display_custom_var(*args):
                for widget in self.custom_var_labelframe.winfo_children():
                    if widget.grid_info()['row'] > 0:
                        widget.destroy()

                if self.selected_item_path.get() != '':
                    if self.n_custom_var.get() != 0:
                        try:
                            list_of_files = glob(self.selected_item_path.get() + '/**/*.txt', recursive=False)
                            custom_file = [x for x in list_of_files if 'Custom' in x]
                            custom_variables = read_table(custom_file[0])
                            info = {}
                            custom_vars = [(key, custom_variables[key]) for key in custom_variables.keys() 
                                                if key not in ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'C_V']]
                        except:
                            info = {"Project": self.selected_item_path.get().split('/')[-3], 
                                    "Subject": self.selected_item_path.get().split('/')[-2], 
                                    "Experiment": self.selected_item_path.get().split('/')[-1], 
                                    "Acquisition_date": "", 
                                    "C_V": ""}
                            custom_vars = [("Group", ""), ("Timepoint", ""), ("Dose", "")]
                            custom_file = [os.path.join(self.selected_item_path.get(), 'MR', self.selected_item_path.get().split('/')[-1] + "_Custom_Variables.txt")]
                        label_list = []
                        entry_list = []
                        for x in range(1, self.n_custom_var.get() + 1):
                            # Custom Variable Label
                            label_n = ttk.Label(self.custom_var_labelframe, text=custom_vars[x-1][0])
                            label_n.grid(row=x, column=0, padx=5, pady=5, sticky=tk.NW)
                            label_list.append(label_n)
                            # Custom Variable Entry
                            entry_n = ttk.Entry(self.custom_var_labelframe, show='', state='disabled')
                            entry_n.var = tk.StringVar()
                            entry_n.var.set(custom_vars[x-1][1])
                            entry_n["textvariable"] = entry_n.var
                            entry_n.grid(row=x, column=1, padx=5, pady=5, sticky=tk.NW)
                            entry_list.append(entry_n)

                        # Button to modify the entry of the custom variable
                        def edit_handler(*args):
                            enable_buttons(entry_list)
                            enable_buttons([confirm_button, reject_button])
                             
                        edit_button = ttk.Button(self.custom_var_labelframe, image=master.logo_edit, command=edit_handler,
                                                    style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        edit_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NW)

                        # Button to confirm changes
                        def accept_changes(*args):
                            # Save change on .txt file
                            data = {}
                            data.update(info)
                            for e in range(len(entry_list)):
                                data[label_list[e]["text"]] = entry_list[e].var.get()
                            write_table(custom_file[0], data)
                            display_custom_var()

                        confirm_button = ttk.Button(self.custom_var_labelframe, image=master.logo_accept, command=accept_changes,
                                                    state='disabled', style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        confirm_button.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NW)

                        # Button to abort changes
                        def reject_changes(*args):
                            # disable_buttons(entry_list)
                            display_custom_var()
                        reject_button = ttk.Button(self.custom_var_labelframe, image=master.logo_delete, command=reject_changes,
                                                    state='disabled', style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        reject_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.NW)

            self.n_custom_var.trace('w', display_custom_var)
            self.selected_item_path.trace('w', display_custom_var)
            #############################################
            ################# Project ###################
            # Menu
            self.project_list_label = ttk.Label(self.frame_uploader, text="Project", font = 'bold', anchor='center')
            self.project_list_label.place(relx = 0.125, rely = 0.65, relwidth=0.15, anchor = N)
            Hovertip(self.project_list_label, "Select an existing project or create a new one ")
            self.OPTIONS = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(self.frame_uploader, self.prj, default_value, *self.OPTIONS)
            self.project_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.project_list.place(relx = 0.05, rely = 0.69, relwidth=0.15, anchor = NW)

            
            # Button to add a new project
            def add_project():
                disable_buttons([self.new_prj_btn])
                createdProject = ProjectManager(self.session)
                master.root.wait_window(createdProject.master)
                if self.session != "":
                    self.session.clearcache()
                self.prj.set(createdProject.project_id.get())
                enable_buttons([self.new_prj_btn])

            self.new_prj_btn = ttk.Button(self.frame_uploader, state=tk.DISABLED, style="Secondary.TButton", image=master.logo_add,
                                        command=add_project, cursor=CURSOR_HAND, text="New Project", compound='left')
            self.new_prj_btn.place(relx = 0.05, rely = 0.75, relwidth=0.15, anchor = NW)
            
            #############################################

            #############################################
            ################# Subject ###################
            # Menu
            if self.prj.get() != '--':
                self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONS2 = []
            self.subject_list_label = ttk.Label(self.frame_uploader, text="Subject", font = 'bold', anchor=CENTER)
            self.subject_list_label.place(relx = 0.5, rely = 0.65, relwidth=0.15, anchor = N)
            Hovertip(self.subject_list_label, "Select an existing subject or create a new one ")
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(self.frame_uploader, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled", cursor=CURSOR_HAND)
            
            self.subject_list.place(relx = 0.5, rely = 0.69, relwidth=0.15, anchor = N)
            
            # Button to add a new subject
            def add_subject():
                disable_buttons([self.new_prj_btn, self.new_sub_btn])
                createdSubject = SubjectManager(self.session)
                master.root.wait_window(createdSubject.master)
                if self.session != "":
                    self.session.clearcache()
                self.prj.set(createdSubject.parent_project.get())
                self.sub.set(createdSubject.subject_id.get())
                enable_buttons([self.new_prj_btn, self.new_sub_btn])

            self.new_sub_btn = ttk.Button(self.frame_uploader, state=tk.DISABLED, style="Secondary.TButton", image=master.logo_add,
                                        command=add_subject, cursor=CURSOR_HAND, text="New Subject", compound='left')
            self.new_sub_btn.place(relx = 0.5, rely = 0.75, relwidth=0.15, anchor = N)
            #############################################

            #############################################
            ################# Experiment ################
            
            # Menu
            if self.prj.get() != '--' and self.sub.get() != '--':
                self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
            else:
                self.OPTIONS3 = []
            self.experiment_list_label = ttk.Label(self.frame_uploader, text="Experiment", font = 'bold', anchor='center')
            self.experiment_list_label.place(relx = 0.875, rely = 0.65, relwidth=0.15, anchor = N)
            Hovertip(self.experiment_list_label, "Select an existing experiment or create a new one ")
            self.exp = tk.StringVar()
            self.experiment_list = ttk.OptionMenu(self.frame_uploader, self.exp, default_value, *self.OPTIONS3)
            self.experiment_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.experiment_list.place(relx = 0.95, rely = 0.69, relwidth=0.15, anchor = NE)
            
            # Button to add a new experiment
            def add_experiment():
                disable_buttons([self.new_prj_btn, self.new_sub_btn, self.new_exp_btn])
                createdExperiment = ExperimentManager(self.session)
                master.root.wait_window(createdExperiment.master)
                if self.session != "":
                    self.session.clearcache()
                self.prj.set(createdExperiment.parent_project.get())
                self.sub.set(createdExperiment.parent_subject.get())
                self.exp.set(createdExperiment.experiment_id.get())
                enable_buttons([self.new_prj_btn, self.new_sub_btn, self.new_exp_btn])

            self.new_exp_btn = ttk.Button(self.frame_uploader, state=tk.DISABLED, style="Secondary.TButton", image=master.logo_add,
                                        text="New Experiment", command=add_experiment, cursor=CURSOR_HAND, compound='left')
            self.new_exp_btn.place(relx = 0.95, rely = 0.75, relwidth=0.15, anchor = NE)
            #############################################

            # Callback methods
            def get_subjects(*args):
                if self.prj.get() != '--' and self.prj.get() in self.OPTIONS:
                    self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
                else:
                    self.OPTIONS2 = []
                self.sub.set(default_value)
                self.exp.set(default_value)
                if self.OPTIONS2 != []:
                    self.subject_list['menu'].delete(0, 'end')
                for key in self.OPTIONS2:
                    self.subject_list['menu'].add_command(label=key, command=lambda var=key:self.sub.set(var))
            def get_experiments(*args):
                if self.prj.get() != '--' and self.sub.get() != '--' and self.prj.get() in self.OPTIONS and self.sub.get() in self.OPTIONS2:
                    self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
                else:
                    self.OPTIONS3 = []
                self.exp.set(default_value)
                if self.OPTIONS3 != []:
                    self.experiment_list['menu'].delete(0, 'end')
                for key in self.OPTIONS3:
                    self.experiment_list['menu'].add_command(label=key, command=lambda var=key:self.exp.set(var))

            self.prj.trace('w', get_subjects)
            self.sub.trace('w', get_experiments)

            #############################################
            ################ EXIT Button ################
            def exit_uploader(*args):
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to exit?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, OptionMenu, ...)
                    destroy_widgets([self.frame_uploader])
                    # Perform disconnection of the session if it is alive
                    try:
                        self.session.disconnect()
                        self.session = ''
                    except:
                        pass
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_text = tk.StringVar() 
            self.exit_btn = ttk.Button(self.frame_uploader, textvariable=self.exit_text, cursor=CURSOR_HAND)
            self.exit_btn.configure(command=exit_uploader)
            self.exit_text.set("Exit")
            self.exit_btn.place(relx = 0.05, rely = 0.9, relwidth=0.1, anchor = NW)
            #############################################

            #############################################
            ################ NEXT Button ################
            def next():
                if self.press_btn == 0:
                    self.project_uploader(master)
                elif self.press_btn == 1:
                    self.subject_uploader(master)
                elif self.press_btn == 2:
                    self.experiment_uploader(master)
                elif self.press_btn == 3:
                    self.file_uploader(master)
                else:
                    pass

            self.next_text = tk.StringVar() 
            self.next_btn = ttk.Button(self.frame_uploader, textvariable=self.next_text, state='disabled',
                                        command=next, cursor=CURSOR_HAND)
            self.next_text.set("Next")
            self.next_btn.place(relx = 0.95, rely = 0.9, relwidth=0.1, anchor = NE)
            #############################################

        def check_buttons(self, master, press_btn=0):

            def back():
                destroy_widgets([self.frame_uploader])
                self.overall_uploader(master)

            # Initialize the press button value
            self.press_btn = press_btn

            # Change the EXIT button into BACK button and modify the command associated with it
            self.exit_text.set("Back")
            self.exit_btn.configure(command=back)

            if press_btn == 0:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn])
                working_text = 'Upload Project'
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                self.folder_to_upload.trace('w', enable_next)
                
            elif press_btn == 1:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn])
                working_text = 'Upload Subject'
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                self.folder_to_upload.trace('w', enable_next)
                
            elif press_btn == 2:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button,
                                self.subject_list, self.new_sub_btn, self.add_file_btn])
                working_text = 'Upload Experiment'
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.sub.trace('w', enable_next)
                self.folder_to_upload.trace('w', enable_next)

            elif press_btn == 3:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button,
                                self.subject_list, self.new_sub_btn,
                                self.experiment_list, self.new_exp_btn, self.add_file_btn])
                working_text = 'Upload File'
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.exp.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.exp.trace('w', enable_next)
                self.folder_to_upload.trace('w', enable_next)
            else:
                pass
            working_label = ttk.Label(self.frame_uploader, text=working_text, font = 'bold', anchor='center')
            working_label.place(relx = 0.5, rely = 0.21, relwidth = 0.18, anchor = CENTER)
        def project_uploader(self, master):

            project_to_upload = self.folder_to_upload.get()
            # Check for empty selected folder
            if os.path.isdir(project_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(project_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                # Start progress bar
                progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Uploader')
                progressbar.start_determinate_bar()

                list_dirs = os.listdir(project_to_upload)

                start_time = time.time()

                def upload_thread():

                    for i, sub in enumerate(list_dirs):
                        progressbar.update_progressbar(i, len(list_dirs))
                        progressbar.show_step(i, len(list_dirs))
                        sub = os.path.join(project_to_upload, sub)

                        list_dirs_exp = os.listdir(sub)
                        for exp in list_dirs_exp:
                            exp = os.path.join(sub, exp)
                            # Check if 'MR' folder is already into the folder_to_upload path
                            if 'MR' != os.path.basename(exp):
                                exp = os.path.join(exp, 'MR').replace('\\', '/')
                            else:
                                exp = exp.replace('\\', '/')
                            params = {}
                            params['folder_to_upload'] = exp
                            params['project_id'] = self.prj.get()
                            params['custom_var_flag'] = self.n_custom_var.get()
                            # Check for existing custom variables file
                            
                            try:
                                # If the custom variables file is available
                                text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                                subject_data = read_table(text_file[0])
                                
                                # Define the subject_id and the experiment_id
                                # Controllo su stringa vuota
                                self.sub.set(subject_data['Subject'])
                                if self.sub.get() != subject_data['Subject']:
                                    ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                            "The subject you are trying to retrieve does not match with the custom variables."
                                                            "\n Would you like to continue?")
                                    if ans != True:
                                        return
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                                        subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()
                                for var in subject_data.keys():
                                    if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date']:
                                        params[var] = subject_data[var]
                            except:
                                # Define the subject_id and the experiment_id if the custom variables file is not available
                                self.sub.set(exp.split('/')[-3].replace('.','_'))
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([exp.split('/')[-4].replace('_dcm', ''), exp.split('/')[-3].replace('.', '_'),
                                                             exp.split('/')[-2].replace('.', '_')]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()

                            progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')

                            self.uploader.upload(params)
                            # Check for Results folder
                            if self.add_file_flag.get() == 1:
                                # self.session.clearcache()
                                self.uploader_file = FileUploader(self.session)
                                progressbar.set_caption('Uploading files to ' + str(self.exp.get()) + ' ...')
                                for sub_dir in os.listdir(exp):
                                    if 'Results' in sub_dir:
                                        vars = {}
                                        vars['project_id'] = self.prj.get()
                                        vars['subject_id'] = self.sub.get()
                                        vars['experiment_id'] = self.exp.get()
                                        vars['folder_name'] = sub_dir
                                        list_of_files = os.scandir(os.path.join(exp, sub_dir))
                                        file_paths = []
                                        for file in list_of_files:
                                            if file.is_file():
                                                file_paths.append(file.path)
                                        self.uploader_file.upload(file_paths, vars)

                self.uploader = Dicom2XnatUploader(self.session)

                t = threading.Thread(target=upload_thread, args=())
                t.start()
                
                while t.is_alive() == True:
                    progressbar.update_bar(0)
                
                # Stop the progress bar and close the popup
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your project is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.label_frame_uploader, self.uploader_data, self.custom_var_labelframe,
                                self.exit_btn, self.next_btn, self.folder_selection_label_frame, self.frame_title])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def subject_uploader(self, master):

            subject_to_upload = self.folder_to_upload.get()
            # Check for empty selected folder
            if os.path.isdir(subject_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(subject_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                list_dirs = os.listdir(subject_to_upload)
                self.uploader = Dicom2XnatUploader(self.session)

                # Start progress bar
                progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Uploader')
                progressbar.start_indeterminate_bar()

                start_time = time.time()

                for exp in list_dirs:
                    exp = os.path.join(subject_to_upload, exp)
                    
                    # Check if 'MR' folder is already into the folder_to_upload path
                    if 'MR' != os.path.basename(exp):
                        exp = os.path.join(exp, 'MR').replace('\\', '/')
                    else:
                        exp = exp.replace('\\', '/')

                    params = {}
                    params['folder_to_upload'] = exp
                    params['project_id'] = self.prj.get()
                    params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(subject_data['Subject'])
                        if self.sub.get() != subject_data['Subject']:
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                    "The subject you are trying to retrieve does not match with the custom variables."
                                                    "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                                    subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date']:
                                params[var] = subject_data[var]
                    except:
                        # Define the subject_id and the experiment_id if the custom variables file is not available
                        if self.sub.get() == '--':
                            self.sub.set(exp.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm',''), exp.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()

                    progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')

                    t = threading.Thread(target=self.uploader.upload, args=(params, ))
                    t.start()

                    while t.is_alive() == True:
                        progressbar.update_bar()
                    else:
                        # Check for Results folder
                        if self.add_file_flag.get() == 1:
                            self.session.clearcache()
                            self.uploader_file = FileUploader(self.session)
                            for sub_dir in os.listdir(exp):
                                if 'Results' in sub_dir:
                                    vars = {}
                                    vars['project_id'] = self.prj.get()
                                    vars['subject_id'] = self.sub.get()
                                    vars['experiment_id'] = self.exp.get()
                                    vars['folder_name'] = sub_dir
                                    list_of_files = os.scandir(os.path.join(exp, sub_dir))
                                    file_paths = []
                                    for file in list_of_files:
                                        if file.is_file():
                                            file_paths.append(file.path)
                                    progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                                    ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                                    ft.start()
                                    while ft.is_alive() == True:
                                        progressbar.update_bar()

                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your subject is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.label_frame_uploader, self.uploader_data, self.custom_var_labelframe,
                                self.exit_btn, self.next_btn, self.folder_selection_label_frame, self.frame_title])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def experiment_uploader(self, master):

            experiment_to_upload = self.folder_to_upload.get()
            # Check for empty selected folder
            if os.path.isdir(experiment_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(experiment_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                try:
                    self.uploader = Dicom2XnatUploader(self.session)
                    # Start progress bar
                    progressbar = ProgressBar(master.root, bar_title='XNAT-PIC Uploader')
                    progressbar.start_indeterminate_bar()

                    start_time = time.time()
                    # Check if 'MR' folder is already into the folder_to_upload path
                    if 'MR' != os.path.basename(experiment_to_upload):
                        experiment_to_upload = os.path.join(experiment_to_upload, 'MR').replace('\\', '/')
                    else:
                        experiment_to_upload = experiment_to_upload.replace('\\', '/')

                    params = {}
                    params['folder_to_upload'] = experiment_to_upload
                    params['project_id'] = self.prj.get()
                    params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(experiment_to_upload, f) for f in os.listdir(experiment_to_upload) if f.endswith('.txt') 
                                                                                                                        and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(subject_data['Subject'])
                        if self.sub.get() != subject_data['Subject']:
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                    "The subject you are trying to retrieve does not match with the custom variables."
                                                    "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                                    subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date']:
                                params[var] = subject_data[var]
                    except:
                        # Define the subject_id and the experiment_id if the custom variables file is not available
                        if self.sub.get() == '--':
                            self.sub.set(experiment_to_upload.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([experiment_to_upload.split('/')[-3].replace('_dcm', ''), 
                                                    experiment_to_upload.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()

                    progressbar.set_caption('Uploading ' + str(self.exp.get()) + ' ...')

                    t = threading.Thread(target=self.uploader.upload, args=(params, ))
                    t.start()

                    while t.is_alive() == True:
                        progressbar.update_bar()
                    else:
                        # Check for Results folder
                        if self.add_file_flag.get() == 1:
                            self.session.clearcache()
                            self.uploader_file = FileUploader(self.session)
                            for sub_dir in os.listdir(experiment_to_upload):
                                if 'Results' in sub_dir:
                                    vars = {}
                                    vars['project_id'] = self.prj.get()
                                    vars['subject_id'] = self.sub.get()
                                    vars['experiment_id'] = self.exp.get()
                                    vars['folder_name'] = sub_dir
                                    list_of_files = os.scandir(os.path.join(experiment_to_upload, sub_dir))
                                    file_paths = []
                                    for file in list_of_files:
                                        if file.is_file():
                                            file_paths.append(file.path)
                                    progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                                    ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                                    ft.start()
                                    while ft.is_alive() == True:
                                        progressbar.update_bar()

                        progressbar.stop_progress_bar()

                        end_time = time.time()
                        print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                except Exception as e: 
                    messagebox.showerror("XNAT-PIC Uploader", e)

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your experiment is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.label_frame_uploader, self.uploader_data, self.custom_var_labelframe,
                                self.exit_btn, self.next_btn, self.folder_selection_label_frame, self.frame_title])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def file_uploader(self, master):

            files_to_upload = os.listdir(self.folder_to_upload.get())
            self.uploader_file = FileUploader(self.session)
            
            if files_to_upload == [] or files_to_upload == '':
                messagebox.showerror('XNAT-PIC Uploader', 'Error! No files selected!')
            else:
                vars = {}
                vars['project_id'] = self.prj.get()
                vars['subject_id'] = self.sub.get()
                vars['experiment_id'] = self.exp.get()
                vars['folder_name'] = self.folder_to_upload.get().split('/')[-1]

                progressbar = ProgressBar(master.root, 'XNAT-PIC File Uploader')
                progressbar.start_indeterminate_bar()

                file_paths = []
                for file in files_to_upload:
                    if os.path.isfile(os.path.join(self.folder_to_upload.get(), file)):
                        file_paths.append(os.path.join(self.folder_to_upload.get(), file))
                        
                progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                ft.start()
                while ft.is_alive() == True:
                    progressbar.update_bar()

                progressbar.stop_progress_bar()
                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your file is uploaded on XNAT platform.")

            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.label_frame_uploader, self.uploader_data, self.custom_var_labelframe,
                                self.exit_btn, self.next_btn, self.folder_selection_label_frame, self.frame_title])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)


if __name__ == "__main__":
    
    freeze_support()
    
    root = tk.Tk()
    check_credentials(root)
    app = xnat_pic_gui(root)
    root.mainloop()

           