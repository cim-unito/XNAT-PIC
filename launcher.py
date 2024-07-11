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
import datetime as dt
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
import xnat
from operator import * 
import webbrowser

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
        try:
            self.root.state('zoomed') # The root widget is adapted to the screen size
        except:
            return
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
        # Load refresh icon
        self.refresh_icon = open_image(PATH_IMAGE + "refresh.png", 15, 15)
        # Load computer icon
        self.computer_icon = open_image(PATH_IMAGE + "computer_icon.png", 15, 15)
        # Load server icon
        self.server_icon = open_image(PATH_IMAGE + "server_icon.png", 15, 15)
        
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
        help_menu = ttk.Menu(self.toolbar_menu, tearoff=0)

        new_menu.add_command(label="Project", image = self.logo_folder, compound = 'left', command=new_prj)
        new_menu.add_command(label="Subject", image = self.logo_folder, compound = 'left',command=new_sub)
        new_menu.add_command(label="Experiment", image = self.logo_folder, compound = 'left',command=new_exp)

        fileMenu.add_cascade(label="New...", image = self.logo_subdirectory, compound = 'left', menu=new_menu)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", image = self.logo_exit, compound = 'left', command=lambda: self.root.destroy())
        
        help_menu.add_command(label="Help", image = self.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))

        self.toolbar_menu.add_cascade(label="File", menu=fileMenu)
        self.toolbar_menu.add_cascade(label="About", menu=help_menu)
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
            #self.xnat_pic_logo_dark = open_image(PATH_IMAGE + "XNAT-PIC_logo.png", 2*self.width/5, self.height/3)
            self.xnat_pic_logo_light = open_image(PATH_IMAGE + "XNAT-PIC-logo-light.png", 2*self.width/5, self.height/3)
            # Load EuroBioimaging icon
            self.eubi_icon = open_image(PATH_IMAGE + "Euro-BioImaging_logo.png", 7*self.width/20, self.height/4)

            if self.frame_label.get() in ["Enter", "Main"]:
                if self.style_label.get() == 'cerculean':
                    self.xnat_pic_logo_label = ttk.Label(self.frame, text="Image dataset transfer to XNAT \nfor preclinical imaging centers", style = "MainTitle.TLabel", justify='center')
                    self.eurobioimaging_logo_label = ttk.Label(self.frame, image=self.eubi_icon)
                else:
                    self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_light)
                self.xnat_pic_logo_label.place(relx=0.6, rely=0.34, anchor=tk.CENTER)
                self.eurobioimaging_logo_label.place(relx=0.6, rely=0.10, anchor=tk.CENTER)

            # Change font according to window size
            if self.width > int(2/3*self.my_width):
                self.style.configure('TButton', font = LARGE_FONT)
                self.style.configure('Title.TLabel', font = ("Helvetica", 36))
                self.style.configure("MainTitle.TLabel", font = ("Helvetica", 36))

            elif self.width > int(self.my_width/3) and self.width < int(2/3*self.my_width):
                self.style.configure('TButton', font = SMALL_FONT)
                self.style.configure('Title.TLabel', font = ("Helvetica", 30))
                self.style.configure("MainTitle.TLabel", font = ("Helvetica", 30))
            
            elif self.width < int(self.my_width/3):
                self.style.configure('TButton', font = SMALL_FONT_2)
                self.style.configure('Title.TLabel', font = ("Helvetica", 24))
                self.style.configure("MainTitle.TLabel", font = ("Helvetica", 24))
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
        self.enter_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.21)
        
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
            help_menu = ttk.Menu(self.toolbar_menu, tearoff=0)

            new_menu.add_command(label="Project", image = self.logo_folder, compound = 'left', command=new_prj)
            new_menu.add_command(label="Subject", image = self.logo_folder, compound = 'left',command=new_sub)
            new_menu.add_command(label="Experiment", image = self.logo_folder, compound = 'left',command=new_exp)

            fileMenu.add_cascade(label="New...", image = self.logo_subdirectory, compound = 'left', menu=new_menu)
            fileMenu.add_separator()
            fileMenu.add_command(label="Exit", image = self.logo_exit, compound = 'left', command=lambda: self.root.destroy())

            help_menu.add_command(label="Help", image = self.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))
            
            self.toolbar_menu.add_cascade(label="File", menu=fileMenu)
            self.toolbar_menu.add_cascade(label="About", menu=help_menu)
            self.root.config(menu=self.toolbar_menu)


        if self.xnat_pic_logo_label.winfo_exists() == 0:
            if self.style_label.get() == 'cerculean':
                self.xnat_pic_logo_label = ttk.Label(self.frame, text="Image dataset transfer to XNAT \nfor preclinical imaging centers", style = "MainTitle.TLabel", justify='center')
                self.eurobioimaging_logo_label = ttk.Label(self.frame, image=self.eubi_icon)
            else:
                self.xnat_pic_logo_label = ttk.Label(self.frame, image=self.xnat_pic_logo_light)
            self.xnat_pic_logo_label.place(relx=0.6, rely=0.34, anchor=tk.CENTER)
            self.eurobioimaging_logo_label.place(relx=0.6, rely=0.10, anchor=tk.CENTER)

        self.frame_label.set("Main")
        # Action buttons           
        # Convert files Bruker2DICOM
        self.convert_btn = ttk.Button(self.frame, text="DICOM Converter",
                                    command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
        self.convert_btn.place(relx=0.6, rely=0.5, anchor=tk.CENTER, relwidth=0.21)
        Hovertip(self.convert_btn,'Convert images from Bruker ParaVision format to DICOM standard')
        
        # Upload files
        def upload_callback(*args):
            self.XNATUploader(self)
        self.upload_btn = ttk.Button(self.frame, text="Uploader",
                                        command=upload_callback, cursor=CURSOR_HAND)
        self.upload_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.21)
        Hovertip(self.upload_btn,'Upload DICOM images to XNAT')

        # Fill in the info
        self.info_btn = ttk.Button(self.frame, text="Edit Custom Forms", 
                                    command=partial(self.metadata, self), cursor=CURSOR_HAND)
        self.info_btn.place(relx=0.6, rely=0.7, anchor=tk.CENTER, relwidth=0.21)
        Hovertip(self.info_btn,'Fill information regarding group, timepoint, etc.')

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
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: exit_converter())

            file_menu.add_command(label="Clear Tree", image = master.logo_clear, compound='left', command = lambda: clear_tree())
            
            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
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
                if self.tree_to_convert.tree.exists(0):
                    self.tree_to_convert.tree.delete(*self.tree_to_convert.tree.get_children())
                if self.tree_converted.tree.exists(0):
                    self.tree_converted.tree.delete(*self.tree_converted.tree.get_children())
                self.conv_flag.set(0)
                self.check_buttons(master, press_btn=0)
            self.prj_conv_btn = ttk.Button(self.frame_converter, text="Convert Project", 
                                            command=prj_conv_handler, cursor=CURSOR_HAND)
            self.prj_conv_btn.place(relx = 0.05, rely = 0.16, relwidth=0.22, anchor = NW)
            Hovertip(self.prj_conv_btn, "Convert a project from Bruker format to DICOM standard")

            # Convert Subject
            def sbj_conv_handler(*args):
                if self.tree_to_convert.tree.exists(0):
                    self.tree_to_convert.tree.delete(*self.tree_to_convert.tree.get_children())
                if self.tree_converted.tree.exists(0):
                    self.tree_converted.tree.delete(*self.tree_converted.tree.get_children())
                self.conv_flag.set(1)
                self.check_buttons(master, press_btn=1)
            self.sbj_conv_btn = ttk.Button(self.frame_converter, text="Convert Subject",
                                            command=sbj_conv_handler, cursor=CURSOR_HAND)
            self.sbj_conv_btn.place(relx = 0.5, rely = 0.16, relwidth=0.22, anchor = N)
            Hovertip(self.sbj_conv_btn, "Convert a subject from Bruker format to DICOM standard")

            # Convert Experiment
            def exp_conv_handler(*args):
                if self.tree_to_convert.tree.exists(0):
                    self.tree_to_convert.tree.delete(*self.tree_to_convert.tree.get_children())
                if self.tree_converted.tree.exists(0):
                    self.tree_converted.tree.delete(*self.tree_converted.tree.get_children())
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
                    return

                # Check if the selected folder is related to the right convertion flag
                if self.conv_flag.get() == 0:
                    if glob(self.folder_to_convert.get() + '//**//**//**//**//**//2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related.\nPlease select an other directory.")
                        disable_buttons([self.next_btn])
                        clear_tree()
                        return
                elif self.conv_flag.get() == 1:
                    if glob(self.folder_to_convert.get() + '//**//**//**//**//2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related.\nPlease select an other directory.")
                        disable_buttons([self.next_btn])
                        clear_tree()
                        return
                elif self.conv_flag.get() == 2:
                    if glob(self.folder_to_convert.get() + '//**//**//**//2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not experiment related.\nPlease select an other directory.")
                        disable_buttons([self.next_btn])
                        clear_tree()
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
                                    cursor=CURSOR_HAND, command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn.place(relx = 0.05, rely = 0.72, anchor = NW)
            Hovertip(self.clear_tree_btn, "Delete tree")
                           
            def selected_object_handler(*args):
                curItem = self.tree_to_convert.tree.focus()
                parentItem = self.tree_to_convert.tree.parent(curItem)
                self.object_folder.set(os.path.join(self.folder_to_convert.get(), self.tree_to_convert.tree.item(parentItem)['text'],
                                    self.tree_to_convert.tree.item(curItem)['text']).replace("\\", "/"))
            self.object_folder = tk.StringVar()

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
            self.clear_tree_btn_post = ttk.Button(self.frame_converter, image=master.logo_clear,
                                    cursor=CURSOR_HAND, state='normal', command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn_post.place(relx = 0.95, rely = 0.72, anchor = NE)
            Hovertip(self.clear_tree_btn_post, "Delete Tree")

            # Treeview widget post_convertion
            self.tree_converted = Treeview(self.frame_converter, columns, width=100)
            self.tree_converted.tree.place(relx = 0.95, rely = 0.48, relheight=0.2, relwidth=0.35, anchor = NE)
            self.tree_converted.scrollbar.place(relx = 0.58, rely = 0.48, relheight=0.2, anchor = NE)

            self.convertion_state.trace('w', tree_thread)

            # EXIT Button 
            def exit_converter():
                result = messagebox.askquestion("XNAT-PIC Converter", "Do you want to go back to home?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, Checkbutton, ...)
                    destroy_widgets([self.frame_converter, self.menu])
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_text = tk.StringVar()
            self.exit_btn = ttk.Button(self.frame_converter, cursor=CURSOR_HAND,
                                    textvariable=self.exit_text,  style="Secondary1.TButton", command=exit_converter)
            self.exit_text.set('Home')
            self.exit_btn.place(relx = 0.05, rely = 0.9, relwidth=0.15, anchor = NW)

            # NEXT Button
            def next_btn_handler(*args):
                if self.conv_flag.get() == 0:
                    self.converted_folder.set(self.folder_to_convert.get() + '_dcm')
                    disable_buttons([self.exit_btn, self.next_btn])
                    self.prj_convertion(master)
     
                elif self.conv_flag.get() == 1:
                   # Popup
                    self.popup_subject = ttk.Toplevel()
                    self.popup_subject.title("XNAT-PIC ~ Converter")
                    master.root.eval(f'tk::PlaceWindow {str(self.popup_subject)} center')
                    self.popup_subject.resizable(False, False)
                    self.popup_subject.grab_set()
                    
                    # If you want the logo 
                    self.popup_subject.iconbitmap(PATH_IMAGE + "logo3.ico")

                    # Select the subjects to copy the Custom Forms to
                    self.popup_subject_frame = ttk.LabelFrame(self.popup_subject, text="Destination path", style="Popup.TLabelframe")
                    self.popup_subject_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

                    # Label     
                    self.popup_subject.label = ttk.Label(self.popup_subject_frame, text="Select the destination path of the converted folder:")  
                    self.popup_subject.label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

                    # List of destination path
                    # The user has the structure prj, sub, exp
                    self.flag_dest_path = IntVar()
                    text_prj_sub_exp = os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-1])  + '_dcm', 
                                                '/'.join(self.folder_to_convert.get().split('/')[-1:]))
                    ttk.Radiobutton(self.popup_subject_frame, variable=self.flag_dest_path, value=1,
                                    text=text_prj_sub_exp.replace("\\","/"), cursor=CURSOR_HAND).grid(row=2, column=0, padx = 5, pady = 5, sticky=W)
                    # The user has only the experiment to convert
                    text_sub = self.folder_to_convert.get() + '_dcm'
                    ttk.Radiobutton(self.popup_subject_frame, variable=self.flag_dest_path, value=2,
                                    text=text_sub, cursor=CURSOR_HAND).grid(row=3, column=0, padx = 5, pady = 5, sticky=W)
                    self.flag_dest_path.set(1)

                    def convert_sub():
                        try:
                            self.popup_subject.destroy()
                        except:
                            pass
                        popup_exp_value = self.flag_dest_path.get()
                        
                        if popup_exp_value == 1:
                            self.converted_folder.set(text_prj_sub_exp)
                        elif popup_exp_value ==2:
                            self.converted_folder.set(text_sub)

                        disable_buttons([self.exit_btn, self.next_btn])
                        self.sbj_convertion(master)
                    self.popup_subject.button_ok = ttk.Button(self.popup_subject, image = master.logo_accept,
                                                command = convert_sub , cursor=CURSOR_HAND)
                    self.popup_subject.button_ok.grid(row=2, column=1, padx=10, pady=5, sticky=NW)
                    # If the popup is closed, it re-enables the buttons
                    def enable():
                        try:
                            self.popup_subject.destroy()
                        except:
                            pass
                        destroy_widgets([self.frame_converter])
                        self.overall_converter(master)
                        
                    self.popup_subject.button_cancel = ttk.Button(self.popup_subject, image = master.logo_delete,
                                                        command = enable, cursor=CURSOR_HAND)
                    self.popup_subject.button_cancel.grid(row=2, column=0, padx=10, pady=5, sticky=NE)

                    self.popup_subject.protocol('WM_DELETE_WINDOW', enable)  
    
                elif self.conv_flag.get() == 2:
                    # Popup
                    self.popup_experiment = ttk.Toplevel()
                    self.popup_experiment.title("XNAT-PIC ~ Converter")
                    master.root.eval(f'tk::PlaceWindow {str(self.popup_experiment)} center')
                    self.popup_experiment.resizable(False, False)
                    self.popup_experiment.grab_set()
                    
                    # If you want the logo 
                    self.popup_experiment.iconbitmap(PATH_IMAGE + "logo3.ico")

                    # Select the subjects to copy the Custom Forms to
                    self.popup_experiment_frame = ttk.LabelFrame(self.popup_experiment, text="Destination path", style="Popup.TLabelframe")
                    self.popup_experiment_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

                    # Label     
                    self.popup_experiment.label = ttk.Label(self.popup_experiment_frame, text="Select the destination path of the converted folder:")  
                    self.popup_experiment.label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

                    # List of destination path
                    # The user has the structure prj, sub, exp
                    self.flag_dest_path = IntVar()
                    text_prj_sub_exp = os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-2])  + '_dcm', 
                                                '/'.join(self.folder_to_convert.get().split('/')[-2:]))
                    ttk.Radiobutton(self.popup_experiment_frame, variable=self.flag_dest_path, value=1,
                                    text=text_prj_sub_exp.replace("\\","/"), cursor=CURSOR_HAND).grid(row=2, column=0, padx = 5, pady = 5, sticky=W)
                    # The user has only the experiment to convert
                    text_exp = self.folder_to_convert.get() + '_dcm'
                    ttk.Radiobutton(self.popup_experiment_frame, variable=self.flag_dest_path, value=2,
                                    text=text_exp, cursor=CURSOR_HAND).grid(row=3, column=0, padx = 5, pady = 5, sticky=W)
                    self.flag_dest_path.set(1)

                    def convert_exp():
                        try:
                            self.popup_experiment.destroy()
                        except:
                            pass
                        popup_exp_value = self.flag_dest_path.get()
                        
                        if popup_exp_value == 1:
                            self.converted_folder.set(text_prj_sub_exp)
                        elif popup_exp_value ==2:
                            self.converted_folder.set(text_exp)

                        disable_buttons([self.exit_btn, self.next_btn])
                        self.exp_convertion(master)
                    self.popup_experiment.button_ok = ttk.Button(self.popup_experiment, image = master.logo_accept,
                                                command = convert_exp , cursor=CURSOR_HAND)
                    self.popup_experiment.button_ok.grid(row=2, column=1, padx=10, pady=5, sticky=NW)
                    # If the popup is closed, it re-enables the buttons
                    def enable():
                        try:
                            self.popup_experiment.destroy()
                        except:
                            pass
                        destroy_widgets([self.frame_converter])
                        self.overall_converter(master)
                        
                    self.popup_experiment.button_cancel = ttk.Button(self.popup_experiment, image = master.logo_delete,
                                                        command = enable, cursor=CURSOR_HAND)
                    self.popup_experiment.button_cancel.grid(row=2, column=0, padx=10, pady=5, sticky=NE)

                    self.popup_experiment.protocol('WM_DELETE_WINDOW', enable)    

                       
                else:
                    self.converted_folder.set('')

                enable_buttons([self.exit_btn])

            self.next_btn = ttk.Button(self.frame_converter, text="Convert", cursor=CURSOR_HAND,  style="Secondary1.TButton", command=next_btn_handler,
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
            enable_buttons([self.select_folder_button, self.clear_tree_btn])

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

            if glob(self.folder_to_convert.get() + '//**//**//**//**//**//2dseq', recursive=False) == []:
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related!")
                return
            
            master.root.deiconify()
            master.root.update()
            # Define the project destination folder
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
                self.conversion_err1 = []
                self.list_scans_err = []
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
                                self.conversion_err1.append(current_folder.split('/')[-1])
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
                            
                            # Delete converted folders that are empty due to exceptions
                            for scan in list_scans:
                                if not os.listdir(scan[1]):
                                    os.rmdir(scan[1])
                                    split_path_list = scan[0].rsplit('/',4)
                                    split_path_str = '/'.join(split_path_list[1:])
                                    self.list_scans_err.append(".../" + split_path_str)

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
            
            str_excep = ''
            if not len(self.conversion_err) == 0:
                str_excep = "Subjects not converted because they already exist and the overwrite flag has not been selected:\n\n" + str([str(x) for x in self.conversion_err])[1:-1]
            str_excep1 = ''
            if not len(self.list_scans_err) == 0:
                str_excep1 = "Scans not converted (check that they are valid Bruker files):\n\n" + str('\n'.join([str(x) for x in self.list_scans_err]))
            str_excep2 = ''
            if not len(self.conversion_err1) == 0:
                str_excep2 = "Scans not converted:\n\n" + str([str(x) for x in self.conversion_err1])[1:-1]

            messagebox.showinfo("XNAT-PIC Converter","The conversion of the project is finished!\n\n\n\n" + 
                                str_excep + "\n\n\n\n" +
                                str_excep1 + "\n\n\n\n" +
                                str_excep2)

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
                    enable_buttons([self.exit_btn])
                    return
            else:
                # Case 2 --> The directory does not exist
                if os.path.exists(self.sub_dst) and os.path.isdir(self.sub_dst):
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
                self.list_scans_err = []
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
                        # Delete converted folders that are empty due to exceptions
                    for scan in list_scans:
                        if not os.listdir(scan[1]):
                            os.rmdir(scan[1])
                            split_path_list = scan[0].rsplit('/',3)
                            split_path_str = '/'.join(split_path_list[1:])
                            self.list_scans_err.append(".../" + split_path_str)
                        
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

            str_excep = ''
            if not len(self.list_scans_err) == 0:
                str_excep = "Scans not converted (check that they are valid Bruker files):\n\n" + str('\n'.join([str(x) for x in self.list_scans_err]))

            messagebox.showinfo("XNAT-PIC Converter","Done! Your subject is successfully converted\n\n\n\n" + str_excep)
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
            self.exp_dst = self.converted_folder.get()

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def exp_converter():
                list_scans = self.converter.get_list_of_folders(self.folder_to_convert.get(), self.exp_dst)
                
                self.list_scans_err = []
                progressbar.set_caption('Converting ' + str(self.folder_to_convert.get().split('/')[-1]) + ' ...')
                with Pool(processes=int(cpu_count() - 1)) as pool:
                    pool.map(self.converter.convert, list_scans)
                for scan in list_scans:
                    if not os.listdir(scan[1]):
                        os.rmdir(scan[1])
                        split_path_list = scan[0].rsplit('/',2)
                        split_path_str = '/'.join(split_path_list[1:])
                        self.list_scans_err.append(".../" + split_path_str)                
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

            str_excep = ''
            if not len(self.list_scans_err) == 0:
                str_excep = "Scans not converted (check that they are valid Bruker files):\n\n" + str('\n'.join([str(x) for x in self.list_scans_err]))

            messagebox.showinfo("XNAT-PIC Converter","Done! Your experiment is successfully converted\n\n\n\n" + str_excep)
            self.convertion_state.set(1)
            enable_buttons([self.exit_btn])

    class XNATUploader():

        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            access_manager = AccessManager(master.root)
            master.root.wait_window(access_manager.popup)
            self.manager = access_manager.login

            if access_manager.connected == False:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            else:
                destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
                self.session = access_manager.session
                self.full_andress = access_manager.popup.entry_address_complete
                self.password = access_manager.popup.entry_password
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
            
            file_menu.add_command(label="Refresh Page", image = master.refresh_icon, compound='left', command = lambda: self.refresh(master))
            file_menu.add_command(label="Clear Tree", image = master.logo_clear, compound='left', command = lambda: clear_tree())
            
            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
            master.root.config(menu=self.menu)


            # Frame Title
            self.frame_title = ttk.Label(self.frame_uploader, text="XNAT-PIC Uploader", style="Title.TLabel", anchor=tk.CENTER)
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)

            # User Icon
            self.user_btn = ttk.Menubutton(self.frame_uploader, text=self.session.logged_in_user, image=master.user_icon, compound='right',
                                                cursor=CURSOR_HAND)
            self.user_btn.menu = Menu(self.user_btn, tearoff=0)
            self.user_btn["menu"] = self.user_btn.menu
            
            self.user_btn.menu.add_command(label="Exit", image = master.logo_exit, compound='left', command=lambda: exit_uploader())
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

            self.separator2 = ttk.Separator(self.frame_uploader, bootstyle="primary")
            self.separator2.place(relx = 0.05, rely = 0.65, relwidth = 0.9, anchor = NW)

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
                    #messagebox.showerror("XNAT-PIC Converter", "Please select a folder.")
                    return
                # Check if the selected folder is related to the right conversion flag
                print(self.folder_to_upload.get())
                print(self.upload_type.get() == 0)
                if self.upload_type.get() == 0 and glob(self.folder_to_upload.get() + "//**//**//**//**//*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not project related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return
                if self.upload_type.get() == 1 and glob(self.folder_to_upload.get() + "//**//**//**//*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not subject related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return
                if self.upload_type.get() == 2 and glob(self.folder_to_upload.get() + "//**//**//*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not experiment related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return

                self.selected_item_path.set('')

            def folder_selected_handler(*args):
                if self.folder_to_upload.get() != '':

                    dict_items = {}

                    # Check for pre-existent tree
                    if self.tree.tree.exists(0):
                        # # Check for the name of the previous tree
                        # If the folder name is changed, then delete the previous tree
                        self.tree.tree.delete(*self.tree.tree.get_children())
                    # If the user wants to upload files, it is not necessary to see the complete tree of the project but only its folder
                    # If the user wants to upload a project, it is not necessary to see the complete tree of the projec. You have the complete tree.
                    if self.upload_type.get() == 0 or self.upload_type.get() == 3:
                        self.chkvar_entire_prj.set(False)
                    if self.chkvar_entire_prj.get():
                        # Define the main folder into the Treeview object
                        if self.upload_type.get() == 0:
                            self.working_folder = self.folder_to_upload.get()
                        elif self.upload_type.get() == 1:
                            self.working_folder = self.folder_to_upload.get().rsplit('/', 1)[0]
                        elif self.upload_type.get() == 2:
                            self.working_folder = self.folder_to_upload.get().rsplit('/', 2)[0]
                        # Scan the folder to get its tree
                        subdir = os.listdir(self.working_folder)
                        # Check for OS configuration files and remove them
                        subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                        
                        j = 0
                        dict_items[str(j)] = {}
                        dict_items[str(j)]['parent'] = ""
                        dict_items[str(j)]['text'] = self.working_folder.split('/')[-1]
                        j = 1
                        for sub in subdirectories:
                            
                            if os.path.isfile(os.path.join(self.working_folder, sub)):
                                # Add the item like a file
                                dict_items[str(j)] = {}
                                dict_items[str(j)]['parent'] = '0'
                                dict_items[str(j)]['text'] = sub
                                dict_items[str(j)]['values'] = ("File")
                                # Update the j counter
                                j += 1

                            elif os.path.isdir(os.path.join(self.working_folder, sub)):
                                branch_idx = j
                                dict_items[str(j)] = {}
                                dict_items[str(j)]['parent'] = '0'
                                dict_items[str(j)]['text'] = sub
                                j += 1
                                # Scansiona le directory interne per ottenere il tree CHIUSO
                                sub_level2 = os.listdir(os.path.join(self.working_folder, sub))
                                subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                                for sub2 in subdirectories2:
                                    if os.path.isfile(os.path.join(self.working_folder, sub, sub2)):
                                        # Add the item like a file
                                        dict_items[str(j)] = {}
                                        dict_items[str(j)]['parent'] = '1'
                                        dict_items[str(j)]['text'] = sub2
                                        dict_items[str(j)]['values'] = ("File")
                                        # Update the j counter
                                        j += 1

                                    elif os.path.isdir(os.path.join(self.working_folder, sub, sub2)):
                                        tmp_exp_path = os.path.join(self.working_folder, sub, sub2)
                                        if glob(tmp_exp_path + "/**/**/*.dcm", recursive=False) == []:
                                            val_exp_1 = "Folder"
                                        else:
                                            val_exp_1 = "Experiment"
                                        dict_items[str(j)] = {}
                                        dict_items[str(j)]['parent'] = '1'
                                        dict_items[str(j)]['text'] = sub2
                                        dict_items[str(j)]['values'] = (val_exp_1)
                                        j += 1

                        # Update the fields of the parent object
                        dict_items['0']['values'] = ("Project")
                        self.tree.set(dict_items)
                    else:
                        # Treeview for the project or experiment
                        if self.upload_type.get() == 0 or self.upload_type.get() == 2:
                            
                            self.working_folder = self.folder_to_upload.get()
                            # Scan the folder to get its tree
                            subdir = os.listdir(self.working_folder)
                            # Check for OS configuration files and remove them
                            subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                        
                            j = 0
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = ""
                            dict_items[str(j)]['text'] = self.working_folder.split('/')[-1]
                            j = 1
                            for sub in subdirectories:
                                
                                if os.path.isfile(os.path.join(self.working_folder, sub)):
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    dict_items[str(j)]['values'] = ("File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.working_folder, sub)):
                                    branch_idx = j
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    j += 1
                                    # Scansiona le directory interne per ottenere il tree CHIUSO
                                    sub_level2 = os.listdir(os.path.join(self.working_folder, sub))
                                    subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                                    for sub2 in subdirectories2:
                                        if os.path.isfile(os.path.join(self.working_folder, sub, sub2)):
                                            # Add the item like a file
                                            dict_items[str(j)] = {}
                                            dict_items[str(j)]['parent'] = '1'
                                            dict_items[str(j)]['text'] = sub2
                                            dict_items[str(j)]['values'] = ("File")
                                            # Update the j counter
                                            j += 1

                                        elif os.path.isdir(os.path.join(self.working_folder, sub, sub2)):
                                            dict_items[str(j)] = {}
                                            dict_items[str(j)]['parent'] = '1'
                                            dict_items[str(j)]['text'] = sub2
                                            if self.upload_type.get() == 0:
                                                tmp_exp_path = os.path.join(self.working_folder, sub, sub2)
                                                if glob(tmp_exp_path + "/**/**/*.dcm", recursive=False) == []:
                                                    dict_items[str(j)]['values'] = ("Folder")
                                                else:
                                                    dict_items[str(j)]['values'] = ("Experiment")
                                            elif self.upload_type.get() == 2:
                                                tmp_exp_path1 = os.path.join(self.working_folder, sub, sub2)
                                                if glob(tmp_exp_path1 + "/*.dcm", recursive=False) == []:
                                                    dict_items[str(j)]['values'] = ("Folder")
                                                else:
                                                    dict_items[str(j)]['values'] = ("Scan")
                                            j += 1
                                    if self.upload_type.get() == 0:    
                                        dict_items[str(branch_idx)]['values'] = ("Subject")
                                    elif self.upload_type.get() == 2:    
                                        dict_items[str(branch_idx)]['values'] = ("Imaging-Technique")

                            # Update the fields of the parent object
                            if self.upload_type.get() == 0:
                                dict_items['0']['values'] = ("Project")
                            if self.upload_type.get() == 2:
                                dict_items['0']['values'] = ("Experiment")
                            
                            self.tree.set(dict_items)
                        # Treeview for the subject
                        if self.upload_type.get() == 1:
                            
                            self.working_folder = self.folder_to_upload.get()
                            subdir = [str(self.folder_to_upload.get().rsplit('/', 1)[1])]
                            # Check for OS configuration files and remove them
                            subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                            # Scan the folder to get its tree
                            subdir = os.listdir(self.working_folder)
                            # Check for OS configuration files and remove them
                            subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                        
                            j = 0
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = ""
                            dict_items[str(j)]['text'] = self.working_folder.split('/')[-1]
                            j = 1
                            for sub in subdirectories:
                                if os.path.isfile(os.path.join(self.working_folder, sub)):
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    dict_items[str(j)]['values'] = ("File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.working_folder, sub)):
                                    tmp_exp_path = os.path.join(self.working_folder, sub)
                                    if glob(tmp_exp_path + "/**/**/*.dcm", recursive=False) == []:
                                        val_exp = "Folder"
                                    else:
                                        val_exp = "Experiment"
                                    branch_idx = j
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    j += 1
                                        
                                    dict_items[str(branch_idx)]['values'] = (val_exp)

                            # Update the fields of the parent object
                            dict_items['0']['values'] = ("Subject")
                            self.tree.set(dict_items)
                        # Treeview for the file
                        if self.upload_type.get() == 3:
                            
                            self.working_folder = self.folder_to_upload.get()
                            subdir = [str(self.folder_to_upload.get().rsplit('/', 1)[1])]
                            # Check for OS configuration files and remove them
                            subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                            # Scan the folder to get its tree
                            subdir = os.listdir(self.working_folder)
                            # Check for OS configuration files and remove them
                            subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                        
                            j = 0
                            dict_items[str(j)] = {}
                            dict_items[str(j)]['parent'] = ""
                            dict_items[str(j)]['text'] = self.working_folder.split('/')[-1]
                            j = 1
                            for sub in subdirectories:
                                if os.path.isfile(os.path.join(self.working_folder, sub)):
                                    # Add the item like a file
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    dict_items[str(j)]['values'] = ("File")
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.working_folder, sub)):
                                    branch_idx = j
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    j += 1
                                        
                                    dict_items[str(branch_idx)]['values'] = ("Folder")

                            # Update the fields of the parent object
                            dict_items['0']['values'] = ("Folder")
                            self.tree.set(dict_items)
                        
            # Initialize the folder_to_upload path
            self.folder_to_upload = tk.StringVar()
            self.select_folder_button = ttk.Button(self.frame_uploader, text="Select folder", style="Secondary.TButton",
                                                    state='disabled', cursor=CURSOR_HAND, command=select_folder)
            self.select_folder_button.place(relx = 0.05, rely = 0.25, relwidth = 0.18, anchor = NW)

            # Treeview for folder visualization
            def get_selected_item(*args):
                selected_item = self.tree.tree.selection()[0]
                self.type_folder = self.tree.tree.item(selected_item, "values")[0]

                if self.working_folder.split('/')[-1] == self.tree.tree.item(selected_item, "text"):
                    self.selected_item_path.set(self.working_folder)
                else:
                    parent_item = self.tree.tree.parent(selected_item)
                    if self.working_folder.split('/')[-1] == self.tree.tree.item(parent_item, "text"):
                        self.selected_item_path.set('/'.join([self.working_folder, 
                                self.tree.tree.item(selected_item, "text")]))
                    else:
                        higher_parent_item = self.tree.tree.parent(parent_item)
                        if self.working_folder.split('/')[-1] == self.tree.tree.item(higher_parent_item, "text"):
                            self.selected_item_path.set('/'.join([self.working_folder, self.tree.tree.item(parent_item, "text"),
                                self.tree.tree.item(selected_item, "text")]))
            
            columns = [("#0", "Folder"), ("#1", "Type")]
            self.tree = Treeview(self.frame_uploader, columns, width=80)
            self.tree.tree.place(relx = 0.29, rely = 0.25, relheight=0.30, relwidth=0.4, anchor = NW)
            self.tree.scrollbar.place(relx = 0.71, rely = 0.25, relheight=0.30, anchor = NE)
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
                    #self.search_entry.config(state='disabled')
                    self.folder_to_upload.set("")
            
            # See the entire project
            self.chkvar_entire_prj = tk.BooleanVar()
            self.chkvar_entire_prj.set(False)
            self.chkbtn_entire_prj = ttk.Checkbutton(self.frame_uploader, text="View the entire project", variable=self.chkvar_entire_prj, command=folder_selected_handler, state='disabled', bootstyle="round-toggle", cursor=CURSOR_HAND)
            self.chkbtn_entire_prj.place(relx = 0.05, rely = 0.30, anchor = NW)
            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = ttk.Checkbutton(self.frame_uploader, variable=self.add_file_flag, onvalue=1, offvalue=0, 
                                text="Additional Files", state='disabled', bootstyle="round-toggle", cursor=CURSOR_HAND)
            self.add_file_btn.place(relx = 0.05, rely = 0.33, anchor = NW)
            
            #############################################
            ################# Project ###################
            # Menu
            self.project_list_label = ttk.Label(self.frame_uploader, text="Project", font = 'bold', anchor='center')
            self.project_list_label.place(relx = 0.125, rely = 0.68, relwidth=0.15, anchor = N)
            Hovertip(self.project_list_label, "Select an existing project or create a new one ")
            self.OPTIONS = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(self.frame_uploader, self.prj, default_value, *self.OPTIONS)
            self.project_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.project_list.place(relx = 0.05, rely = 0.72, relwidth=0.15, anchor = NW)

            
            # Button to add a new project
            def add_project():
                #disable_buttons([self.new_prj_btn])
                createdProject = ProjectManager(self.session)
                master.root.wait_window(createdProject.master)
                if self.session != "":
                    self.session.clearcache()
                self.prj.set(createdProject.project_id.get())
                #enable_buttons([self.new_prj_btn])

            self.new_prj_btn = ttk.Button(self.frame_uploader, state=tk.DISABLED, style="Secondary.TButton", image=master.logo_add,
                                        command=add_project, cursor=CURSOR_HAND, text="New Project", compound='left')
            self.new_prj_btn.place(relx = 0.05, rely = 0.78, relwidth=0.15, anchor = NW)
            
            #############################################

            #############################################
            ################# Subject ###################
            # Menu
            if self.prj.get() != '--':
                self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONS2 = []
            self.subject_list_label = ttk.Label(self.frame_uploader, text="Subject", font = 'bold', anchor=CENTER)
            self.subject_list_label.place(relx = 0.5, rely = 0.68, relwidth=0.15, anchor = N)
            Hovertip(self.subject_list_label, "Select an existing subject or create a new one ")
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(self.frame_uploader, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.subject_list.place(relx = 0.5, rely = 0.72, relwidth=0.15, anchor = N)
            
            # Button to add a new subject
            def add_subject():
                #disable_buttons([self.new_prj_btn, self.new_sub_btn])
                createdSubject = SubjectManager(self.session)
                master.root.wait_window(createdSubject.master)
                if self.session != "":
                    self.session.clearcache()
                self.prj.set(createdSubject.parent_project.get())
                self.sub.set(createdSubject.subject_id.get())
                #enable_buttons([self.new_prj_btn, self.new_sub_btn])

            self.new_sub_btn = ttk.Button(self.frame_uploader, state=tk.DISABLED, style="Secondary.TButton", image=master.logo_add,
                                        command=add_subject, cursor=CURSOR_HAND, text="New Subject", compound='left')
            self.new_sub_btn.place(relx = 0.5, rely = 0.78, relwidth=0.15, anchor = N)
            #############################################

            #############################################
            ################# Experiment ################
            # Menu
            if self.prj.get() != '--' and self.sub.get() != '--':
                self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
            else:
                self.OPTIONS3 = []
            self.experiment_list_label = ttk.Label(self.frame_uploader, text="Experiment", font = 'bold', anchor='center')
            self.experiment_list_label.place(relx = 0.875, rely = 0.68, relwidth=0.15, anchor = N)
            Hovertip(self.experiment_list_label, "Select an existing experiment or create a new one ")
            self.exp = tk.StringVar()
            self.experiment_list = ttk.OptionMenu(self.frame_uploader, self.exp, default_value, *self.OPTIONS3)
            self.experiment_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.experiment_list.place(relx = 0.95, rely = 0.72, relwidth=0.15, anchor = NE)
            
            # Button to add a new experiment
            def add_experiment():
                #disable_buttons([self.new_prj_btn, self.new_sub_btn, self.new_exp_btn])
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
            self.new_exp_btn.place(relx = 0.95, rely = 0.78, relwidth=0.15, anchor = NE)
            #############################################

            # Callback methods
            def get_subjects(*args):
                if self.prj.get() != '--' and self.prj.get() in self.OPTIONS:
                    self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
                else:
                    self.OPTIONS2 = []
                self.sub.set(default_value)
                self.exp.set(default_value)
                self.subject_list['menu'].delete(0, 'end')
                for key in self.OPTIONS2:
                    self.subject_list['menu'].add_command(label=key, command=lambda var=key:self.sub.set(var))
            def get_experiments(*args):
                if self.prj.get() != '--' and self.sub.get() != '--' and self.prj.get() in self.OPTIONS and self.sub.get() in self.OPTIONS2:
                    self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
                else:
                    self.OPTIONS3 = []
                self.exp.set(default_value)
                self.experiment_list['menu'].delete(0, 'end')
                for key in self.OPTIONS3:
                    self.experiment_list['menu'].add_command(label=key, command=lambda var=key:self.exp.set(var))

            self.prj.trace('w', get_subjects)
            self.sub.trace('w', get_experiments)

            #############################################
            ################ EXIT Button ################
            def exit_uploader(*args):
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to go back to home?", icon='warning')
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
            self.exit_btn = ttk.Button(self.frame_uploader, textvariable=self.exit_text, cursor=CURSOR_HAND, style="Secondary1.TButton")
            self.exit_btn.configure(command=exit_uploader)
            self.exit_text.set("Home")
            self.exit_btn.place(relx = 0.05, rely = 0.9, relwidth=0.15, anchor = NW)
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
                                        command=next, cursor=CURSOR_HAND, style="Secondary1.TButton")
            self.next_text.set("Upload")
            self.next_btn.place(relx = 0.95, rely = 0.9, relwidth=0.15, anchor = NE)
        #############################################
        ################ Refresh Button ################
        def refresh(self, master):
            self.session = AccessManager.reconnect(self.full_andress, self.session.logged_in_user, self.password)
            
            destroy_widgets([self.frame_uploader])
            self.overall_uploader(master)

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
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn, self.chkbtn_entire_prj])
                working_text = 'Upload Project from your PC...'
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
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn, self.chkbtn_entire_prj])
                working_text = 'Upload Subject from your PC...'
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
                                self.subject_list, self.new_sub_btn, self.add_file_btn, self.chkbtn_entire_prj])
                working_text = 'Upload Experiment from your PC...'
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
                                self.experiment_list, self.new_exp_btn, self.add_file_btn, self.chkbtn_entire_prj])
                working_text = 'Upload File from your PC...'
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
            working_label = ttk.Label(self.frame_uploader, text=working_text, image = master.computer_icon, compound=tk.LEFT, font = 'bold', anchor='center')
            working_label.place(relx = 0.5, rely = 0.21, relwidth = 0.3, anchor = CENTER)
            working_label1 = ttk.Label(self.frame_uploader, text="...to XNAT", image = master.server_icon, compound=tk.RIGHT, font = 'bold', anchor='center')
            working_label1.place(relx = 0.5, rely = 0.65, relwidth = 0.18, anchor = CENTER)

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
                            
                            try:
                                # Define the subject_id and the experiment_id 
                                self.sub.set(exp.split('/')[-3].replace('.','_'))
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([exp.split('/')[-4].replace('_dcm', ''), exp.split('/')[-3].replace('.', '_'),
                                                             exp.split('/')[-2].replace('.', '_')]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()
                                
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                                raise

                            progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')
                            
                            self.uploader.upload(params)
                            # Check for Results folder
                            if self.add_file_flag.get() == 1:
                                # self.session.clearcache()
                                self.uploader_file = FileUploader(self.session)
                                progressbar.set_caption('Uploading files to ' + str(self.exp.get()) + ' ...')
                                for sub_dir in os.listdir(exp):
                                    if 'Results'.lower() in sub_dir.lower():
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
            destroy_widgets([self.frame_uploader, self.menu])
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

                    try:
                        # Define the subject_id and the experiment_id 
                        if self.sub.get() == '--':
                            self.sub.set(exp.split('/')[-3].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm',''), exp.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                        raise

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
                                if 'Results'.lower() in sub_dir.lower():
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
            destroy_widgets([self.frame_uploader, self.menu])
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

                    try:
                        # Define the subject_id and the experiment_id 
                        if self.sub.get() == '--':
                            self.sub.set(experiment_to_upload.split('/')[-3].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([experiment_to_upload.split('/')[-3].replace('_dcm', ''), 
                                                    experiment_to_upload.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                        raise

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
                                if 'Results'.lower() in sub_dir.lower():
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
                    raise

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your experiment is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.frame_uploader, self.menu])
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
            destroy_widgets([self.frame_uploader, self.menu])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)
    
    # Fill in information
    class metadata():
        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            access_manager = AccessManager(master.root)
            master.root.wait_window(access_manager.popup)
            self.manager = access_manager.login

            if access_manager.connected == False:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            else:
                destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
                self.session = access_manager.session
                self.full_andress = access_manager.popup.entry_address_complete
                self.password = access_manager.popup.entry_password
                self.overall_projectdata(master)
 
        def overall_projectdata(self, master):
            
            # Create new frame
            master.frame_label.set("Edit Custom Forms")
            
            ################################### Menu bar ###################################
            self.menu = ttk.Menu(master.root)
            home_menu = ttk.Menu(self.menu, tearoff=0)
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: self.home_metadata(master))
            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))
            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="About", menu=help_menu)

            master.root.config(menu=self.menu)

            # Label Frame Main (for Title only)
            self.frame_metadata = ttk.Frame(master.frame, style="Hidden.TLabelframe")
            self.frame_metadata.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)
            # Frame Title
            self.frame_title = ttk.Label(self.frame_metadata, text="Edit Custom Forms", style='Title.TLabel')
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)
            
            # User Icon
            self.user_btn = ttk.Menubutton(self.frame_metadata, text=self.session.logged_in_user, image=master.user_icon, compound='right',
                                                cursor=CURSOR_HAND)
            self.user_btn.menu = Menu(self.user_btn, tearoff=0)
            self.user_btn["menu"] = self.user_btn.menu
            
            self.user_btn.menu.add_command(label="Exit", image = master.logo_exit, compound='left', command = lambda: self.home_metadata(master))
            self.user_btn.place(relx = 0.95, rely = 0.05, anchor = NE)
            
            ################################### Project, Subject, Experiment buttons ###################################
            # Select a  Project
            # Initialize variables
            self.metadata_type = tk.IntVar()
            def prj_data_handler(*args):
                self.metadata_type.set(0)
                self.check_buttons(master, press_btn=0)
            self.prj_data_btn = ttk.Button(self.frame_metadata, text="Project", 
                                            command=prj_data_handler, cursor=CURSOR_HAND)
            self.prj_data_btn.place(relx = 0.05, rely = 0.12, relwidth=0.22, anchor = NW)
            Hovertip(self.prj_data_btn, "Select a project to add Custom Forms")

            # Select a Subject
            def sbj_data_handler(*args):
                self.metadata_type.set(1)
                self.check_buttons(master, press_btn=1)
            self.sbj_data_btn = ttk.Button(self.frame_metadata, text="Subject",
                                            command=sbj_data_handler, cursor=CURSOR_HAND)
            self.sbj_data_btn.place(relx = 0.5, rely = 0.12, relwidth=0.22, anchor = N)
            Hovertip(self.sbj_data_btn, "Select a subject to add Custom Forms")

            # Select a Experiment
            def exp_data_handler(*args):
                self.metadata_type.set(2)
                self.check_buttons(master, press_btn=2)
            self.exp_data_btn = ttk.Button(self.frame_metadata, text="Experiment",
                                            command=exp_data_handler, cursor=CURSOR_HAND)
            self.exp_data_btn.place(relx = 0.95, rely = 0.12, relwidth=0.22, anchor = NE)
            Hovertip(self.exp_data_btn, "Select a experiment to add Custom Forms")

            self.separator1 = ttk.Separator(self.frame_metadata, bootstyle="primary")
            self.separator1.place(relx = 0.05, rely = 0.21, relwidth = 0.9, anchor = NW)
            
            ################################### Project, Subject, Experiment Lists ###################################
            ################# Project ###################
            # Menu
            self.project_list_label = ttk.Label(self.frame_metadata, text="Project", font = 'bold', anchor='center')
            self.project_list_label.place(relx = 0.16, rely = 0.26, relwidth=0.15, anchor = N)
            Hovertip(self.project_list_label, "Select an existing project")
            self.OPTIONSPRJ = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(self.frame_metadata, self.prj, default_value, *self.OPTIONSPRJ)
            self.project_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.project_list.place(relx = 0.16, rely = 0.30, relwidth=0.15, anchor = N)
            ################# Subject ###################
            # Menu
            if self.prj.get() != '--':
                self.OPTIONSSBJ = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONSSBJ = []
            self.subject_list_label = ttk.Label(self.frame_metadata, text="Subject", font = 'bold', anchor=CENTER)
            self.subject_list_label.place(relx = 0.5, rely = 0.26, relwidth=0.15, anchor = N)
            Hovertip(self.subject_list_label, "Select an existing subject")
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(self.frame_metadata, self.sub, default_value, *self.OPTIONSSBJ)
            self.subject_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.subject_list.place(relx = 0.5, rely = 0.30, relwidth=0.15, anchor = N)
            ################# Experiment ################
            # Menu
            if self.prj.get() != '--' and self.sub.get() != '--':
                self.OPTIONSEXP = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
            else:
                self.OPTIONSEXP = []
            self.experiment_list_label = ttk.Label(self.frame_metadata, text="Experiment", font = 'bold', anchor='center')
            self.experiment_list_label.place(relx = 0.84, rely = 0.26, relwidth=0.15, anchor = N)
            Hovertip(self.experiment_list_label, "Select an existing experiment")
            self.exp = tk.StringVar()
            self.experiment_list = ttk.OptionMenu(self.frame_metadata, self.exp, default_value, *self.OPTIONSEXP)
            self.experiment_list.configure(state="disabled", cursor=CURSOR_HAND)
            self.experiment_list.place(relx = 0.84, rely = 0.30, relwidth=0.15, anchor = N)

            ################################### Custom Forms ###################################
            #self.separator2 = ttk.Separator(self.frame_metadata, bootstyle="primary")
            #self.separator2.place(relx = 0.05, rely = 0.40, relwidth = 0.9, anchor = NW)
            self.CF_label = ttk.Label(self.frame_metadata, text = "Custom Forms", font = SMALL_FONT)
            self.CF_label.place(relx = 0.5, rely = 0.40, anchor = CENTER)
            
            #### Group ####
            self.group_label = ttk.Label(self.frame_metadata, text = "Group", font = SMALL_FONT)
            self.group_label.place(relx = 0.33, rely = 0.45, anchor = N)
            self.group_entry = ttk.Entry(self.frame_metadata, takefocus = 0, state='disabled', bootstyle="light")
            self.group_entry.place(relx = 0.5, rely = 0.45, anchor = N, relwidth=0.22)
            # Group Menu
            self.default_value1 = ""
            self.OPTIONS0 = ["untreated", "treated"]
            self.selected_group = tk.StringVar()
            self.selected_group.set("")
            self.group_menu = ttk.OptionMenu(self.frame_metadata, self.selected_group, self.default_value1, *self.OPTIONS0)
            self.group_menu['state'] = 'disabled'
            self.group_menu.place(relx = 0.61, rely = 0.49, anchor = NE, relwidth=0.08)
            
            #### Timepoint ####
            self.timepoint_label = ttk.Label(self.frame_metadata, text = "Timepoint", font = SMALL_FONT)
            self.timepoint_label.place(relx = 0.33, rely = 0.55, anchor = N)
            self.timepoint_entry = ttk.Entry(self.frame_metadata, state='disabled', takefocus = 0, bootstyle="light")
            self.timepoint_entry.place(relx = 0.5, rely = 0.55, anchor = N, relwidth=0.22)
            # Timepoint menu
            self.OPTIONS1 = ["pre", "post"]
            self.default_value1 = ""
            self.selected_timepoint = tk.StringVar()
            self.selected_timepoint.set("")
            self.timepoint_menu = ttk.OptionMenu(self.frame_metadata, self.selected_timepoint, self.default_value1, *self.OPTIONS1)
            self.timepoint_menu['state'] = 'disabled'
            self.timepoint_menu.place(relx = 0.39, rely = 0.59, anchor = NW, relwidth=0.06)
            
            self.time_entry_value = tk.StringVar()
            self.time_entry = ttk.Entry(self.frame_metadata, state='disabled', takefocus = 0, textvariable=self.time_entry_value, bootstyle="light")
            self.time_entry.place(relx = 0.5, rely = 0.59, anchor = N, relwidth=0.06)

            self.OPTIONS2 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
            self.selected_timepoint1 = tk.StringVar()
            self.selected_timepoint1.set("")
            self.timepoint_menu1 = ttk.OptionMenu(self.frame_metadata, self.selected_timepoint1, self.default_value1, *self.OPTIONS2)
            self.timepoint_menu1['state'] = 'disabled'
            self.timepoint_menu1.place(relx = 0.61, rely = 0.59, anchor = NE, relwidth=0.06)
            
            #### Dose ####
            self.dose_label = ttk.Label(self.frame_metadata, text = "Dose", font = SMALL_FONT)
            self.dose_label.place(relx = 0.33, rely = 0.65, anchor = N)
            self.dose_entry = ttk.Entry(self.frame_metadata, state='disabled', takefocus = 0, bootstyle="light")
            self.dose_entry.place(relx = 0.5, rely = 0.65, anchor = N, relwidth=0.22)
            # Dose
            self.dose_entry_value = tk.StringVar()
            self.dose_entry1 = ttk.Entry(self.frame_metadata, state='disabled', takefocus = 0, textvariable=self.dose_entry_value, bootstyle="light")
            self.dose_entry1.place(relx = 0.5, rely = 0.69, anchor = N, relwidth=0.06)

            self.OPTIONS3 = ["mg/kg"]
            self.selected_dose = tk.StringVar()
            self.selected_dose.set("")
            self.dose_menu = ttk.OptionMenu(self.frame_metadata, self.selected_dose, self.default_value1, *self.OPTIONS3)
            self.dose_menu['state'] = 'disabled'
            self.dose_menu.place(relx = 0.61, rely = 0.69, anchor = NE, relwidth=0.06)
            
            ################ Callback methods ################
            def get_subjects(*args):
                if self.prj.get() != '--' and self.prj.get() in self.OPTIONSPRJ:
                    self.OPTIONSSBJ = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
                else:
                    self.OPTIONSSBJ = []
                self.sub.set(default_value)
                self.exp.set(default_value)
                self.subject_list['menu'].delete(0, 'end')
                for key in self.OPTIONSSBJ:
                    self.subject_list['menu'].add_command(label=key, command=lambda var=key:self.sub.set(var))
            def get_experiments(*args):
                if self.prj.get() != '--' and self.sub.get() != '--' and self.prj.get() in self.OPTIONSPRJ and self.sub.get() in self.OPTIONSSBJ:
                    self.OPTIONSEXP = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
                else:
                    self.OPTIONSEXP = []
                self.exp.set(default_value)
                self.experiment_list['menu'].delete(0, 'end')
                for key in self.OPTIONSEXP:
                    self.experiment_list['menu'].add_command(label=key, command=lambda var=key:self.exp.set(var))

            self.prj.trace_add('write', get_subjects)
            self.sub.trace_add('write', get_experiments)

            ################ EXIT Button ################
            self.exit_text = tk.StringVar() 
            self.exit_btn = ttk.Button(self.frame_metadata, textvariable=self.exit_text, command = lambda: self.home_metadata(master), cursor=CURSOR_HAND, style="Secondary1.TButton")
            self.exit_text.set("Home")
            self.exit_btn.place(relx = 0.05, rely = 0.9, relwidth=0.15, anchor = NW)
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
            self.next_btn = ttk.Button(self.frame_metadata, textvariable=self.next_text, state='disabled',
                                        command=next, cursor=CURSOR_HAND, style="Secondary1.TButton")
            self.next_text.set("Save")
            self.next_btn.place(relx = 0.95, rely = 0.9, relwidth=0.15, anchor = NE)

        def check_buttons(self, master, press_btn=0):

            def back():
                destroy_widgets([self.frame_metadata])
                self.overall_projectdata(master)

            # Initialize the press button value
            self.press_btn = press_btn

            # Change the EXIT button into BACK button and modify the command associated with it
            self.exit_text.set("Back")
            self.exit_btn.configure(command=back)

            def unlock_widgets():
                self.group_entry.config(bootstyle='primary')
                self.timepoint_entry.config(bootstyle='primary')
                self.dose_entry.config(bootstyle='primary')
                self.time_entry.config(bootstyle='primary')
                self.dose_entry1.config(bootstyle='primary')
                enable_buttons([self.group_entry, self.group_menu, self.timepoint_entry, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_entry, self.dose_entry1, self.dose_menu])   

            def get_custom_form_GUI(custom_forms_value):
                    self.group_entry.delete(0,END)
                    self.group_entry.insert(0,custom_forms_value[0])
                    self.timepoint_entry.delete(0,END)
                    self.timepoint_entry.insert(0,custom_forms_value[1])
                    self.dose_entry.delete(0,END)
                    self.dose_entry.insert(0,custom_forms_value[2])
                    # Clear option menu
                    self.selected_group.set("")
                    self.selected_timepoint.set("")
                    self.selected_timepoint1.set("")
                    self.selected_dose.set("")
                    self.time_entry.delete(0,END)
                    self.dose_entry1.delete(0,END)
                    self.group_entry.focus()

            if press_btn == 0:
                # Disable main buttons
                disable_buttons([self.prj_data_btn , self.sbj_data_btn , self.exp_data_btn])
                enable_buttons([self.project_list])   
                # Enable NEXT button only if all the requested fields are filled
                
                def enable_next(*args):
                    if self.prj.get() != '--':
                        try:
                            unlock_widgets()
                            custom_forms_value = get_custom_forms(self.session,  self.press_btn, self.prj.get())
                            get_custom_form_GUI(custom_forms_value)
                        except Exception as e:
                            messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                            raise
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.prj.trace_add('write', enable_next)
                
            elif press_btn == 1:
                # Disable main buttons
                disable_buttons([self.prj_data_btn , self.sbj_data_btn , self.exp_data_btn])
                enable_buttons([self.project_list, self.subject_list])   

                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--':
                        try:
                            unlock_widgets()
                            custom_forms_value = get_custom_forms(self.session,  self.press_btn, self.prj.get(), self.sub.get())
                            get_custom_form_GUI(custom_forms_value)
                        except Exception as e:
                            messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                            raise
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.sub.trace_add('write', enable_next)
                
            elif press_btn == 2:
                # Disable main buttons
                disable_buttons([self.prj_data_btn , self.sbj_data_btn , self.exp_data_btn])
                enable_buttons([self.project_list, self.subject_list, self.experiment_list])   
                
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.exp.get() != '--':
                        try:
                            unlock_widgets()
                            custom_forms_value = get_custom_forms(self.session,  self.press_btn, self.prj.get(), self.sub.get(), self.exp.get() != '--')
                            get_custom_form_GUI(custom_forms_value)
                        except Exception as e:
                            messagebox.showerror("XNAT-PIC", "Error: " + str(e))  
                            raise
                        enable_buttons([self.next_btn])
                    else:
                        disable_buttons([self.next_btn])
                self.exp.trace_add('write', enable_next)

        ##################### Exit the metadata ####################
        def home_metadata(self, master):
            result = messagebox.askquestion("Exit", "Do you want to go back to home?", icon='warning')
            if result == 'yes':
                destroy_widgets([self.frame_metadata, self.menu])
                # Perform disconnection of the session if it is alive
                try:
                    self.session.disconnect()
                    self.session = ''
                except:
                    pass
                # Restore the main frame
                xnat_pic_gui.choose_your_action(master)
                master.root.after(2000, xnat_pic_gui.choose_your_action(master))

if __name__ == "__main__":
    
    freeze_support()
    
    root = tk.Tk()
    check_credentials(root)
    app = xnat_pic_gui(root)
    root.mainloop()

           