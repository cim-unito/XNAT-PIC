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
        
        # Fill in the info
        self.info_btn = ttk.Button(self.frame, text="Edit Custom Variables", 
                                    command=partial(self.metadata, self), cursor=CURSOR_HAND)
        self.info_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.21)
        Hovertip(self.info_btn,'Fill information regarding group, timepoint, etc.')

        # Upload files
        def upload_callback(*args):
            self.XNATUploader(self)
        self.upload_btn = ttk.Button(self.frame, text="Uploader",
                                        command=upload_callback, cursor=CURSOR_HAND)
        self.upload_btn.place(relx=0.6, rely=0.7, anchor=tk.CENTER, relwidth=0.21)
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
                    if glob(self.folder_to_convert.get() + '/**/**/**/**/**/2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related.\nPlease select an other directory.")
                        disable_buttons([self.next_btn])
                        clear_tree()
                        return
                elif self.conv_flag.get() == 1:
                    if glob(self.folder_to_convert.get() + '/**/**/**/**/2dseq', recursive=False) == []:
                        messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related.\nPlease select an other directory.")
                        disable_buttons([self.next_btn])
                        clear_tree()
                        return
                elif self.conv_flag.get() == 2:
                    if glob(self.folder_to_convert.get() + '/**/**/**/2dseq', recursive=False) == []:
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

                    # Select the subjects to copy the custom variables to
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

                    # Select the subjects to copy the custom variables to
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

            if glob(self.folder_to_convert.get() + '/**/**/**/**/**/2dseq', recursive=False) == []:
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
                 
    # Fill in information
    class metadata():
        def __init__(self, master):
            try:
                destroy_widgets([master.toolbar_menu, master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo_label])
            except:
                pass
            self.overall_projectdata(master)

        def overall_projectdata(self, master):
            
            # Create new frame
            master.frame_label.set("Edit Custom Variables")
            
            # Menu bar
            self.menu = ttk.Menu(master.root)
            file_menu = ttk.Menu(self.menu, tearoff=0)
            clear_menu = ttk.Menu(self.menu, tearoff=0)
            modify_ID_menu = ttk.Menu(self.menu, tearoff=0)
            home_menu = ttk.Menu(self.menu, tearoff=0)
            help_menu = ttk.Menu(self.menu, tearoff=0)

            home_menu.add_command(label="Home", image = master.logo_home, compound='left', command = lambda: self.home_metadata(master))

            modify_ID_menu.add_command(label="Project", compound='left', command = lambda: self.modify_ID_metadata(master, flag_ID='Project'))
            modify_ID_menu.add_command(label="Subject", compound='left', command = lambda: self.modify_ID_metadata(master, flag_ID='Subject'))
            modify_ID_menu.add_command(label="Experiment", compound='left', command = lambda: self.modify_ID_metadata(master, flag_ID='Experiment'))
            modify_ID_menu.add_command(label="Acquisition Date", compound='left', command = lambda: self.modify_ID_metadata(master, flag_ID='Acquisition Date'))
            file_menu.add_cascade(label="Modify Name ID", image = master.logo_edit, compound='left', menu=modify_ID_menu)
            file_menu.add_separator()
            file_menu.add_command(label="Add Custom Variable", image = master.logo_add, compound='left', command = lambda: self.add_custom_variable(master))
            file_menu.add_separator()
            clear_menu.add_command(label="Group", compound='left', command = lambda: self.clear_metadata(flag='Group'))
            clear_menu.add_command(label="Timepoint", compound='left', command = lambda: self.clear_metadata(flag='Timepoint'))
            clear_menu.add_command(label="Dose", compound='left', command = lambda: self.clear_metadata(flag='Dose'))
            clear_menu.add_command(label="All", compound='left', command = lambda: self.clear_metadata(flag='All'))
            file_menu.add_cascade(label="Clear Custom Variables", image = master.logo_clear, compound='left', menu=clear_menu)
            file_menu.add_separator()
            file_menu.add_command(label="Save All", image = master.logo_save, compound='left', command = lambda: self.save_metadata())

            help_menu.add_command(label="Help", image = master.logo_help, compound='left', command = lambda: webbrowser.open('https://www.cim.unito.it/website/research/research_xnat.php'))

            self.menu.add_cascade(label='Home', menu=home_menu)
            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_cascade(label="About", menu=help_menu)
            master.root.config(menu=self.menu)

            # Label Frame Main (for Title only)
            self.frame_metadata = ttk.Frame(master.frame, style="Hidden.TLabelframe")
            self.frame_metadata.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)
            # Frame Title
            self.frame_title = ttk.Label(self.frame_metadata, text="Edit Custom Variables", style='Title.TLabel')
            self.frame_title.place(relx = 0.5, rely = 0.05, anchor = CENTER)
            
            # Select a  Project
            def prj_data_handler(*args):
                self.select_button(master, press_btn='Project')
            self.prj_data_btn = ttk.Button(self.frame_metadata, text="Select Project", 
                                            command=prj_data_handler, cursor=CURSOR_HAND)
            self.prj_data_btn.place(relx = 0.05, rely = 0.12, relwidth=0.22, anchor = NW)
            Hovertip(self.prj_data_btn, "Select a project to add custom variables")

            # Select a Subject
            def sbj_data_handler(*args):
                self.select_button(master, press_btn='Subject')
            self.sbj_data_btn = ttk.Button(self.frame_metadata, text="Select Subject",
                                            command=sbj_data_handler, cursor=CURSOR_HAND)
            self.sbj_data_btn.place(relx = 0.5, rely = 0.12, relwidth=0.22, anchor = N)
            Hovertip(self.sbj_data_btn, "Select a subject to add custom variables")

            # Select a Experiment
            def exp_data_handler(*args):
                self.select_button(master, press_btn='Experiment')
            self.exp_data_btn = ttk.Button(self.frame_metadata, text="Select Experiment",
                                            command=exp_data_handler, cursor=CURSOR_HAND)
            self.exp_data_btn.place(relx = 0.95, rely = 0.12, relwidth=0.22, anchor = NE)
            Hovertip(self.exp_data_btn, "Select a experiment to add custom variables")

            self.separator1 = ttk.Separator(self.frame_metadata, bootstyle="primary")
            self.separator1.place(relx = 0.05, rely = 0.21, relwidth = 0.9, anchor = NW)

            # Create the frame
            self.notebook = ScrollableNotebook(self.frame_metadata, wheelscroll=True, tabmenu=True)
            self.notebook.place(relx = 0.05, rely = 0.25, relheight=0.25, relwidth=0.34, anchor = tk.NW)
                       
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
            self.label_frame_ID.place(relx = 0.5, rely = 0.25, relheight=0.25, relwidth=0.37, anchor = tk.NW)
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            keys_ID = ["Project", "Subject"]
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
                self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width= 20 if key == "Acquisition_Date" else 44))
                self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            #####################################################################
            # Choose at which level to add the custom variables
            self.label_frame_level = ttk.LabelFrame(self.frame_metadata, text="Custom Variables", padding = 5, bootstyle="primary") 
            #self.label_level.place(relx = 0.05, rely = 0.6, relwidth = 0.34, anchor = tk.NW)
            
            # Scroll bar in the Label frame CV
            self.canvas_level = tk.Canvas(self.label_frame_level)
            self.frame_level = tk.Frame(self.canvas_level)
            
            self.vsb_level = ttk.Scrollbar(self.label_frame_level, orient="vertical", command=self.canvas_level.yview)
            self.canvas_level.configure(yscrollcommand=self.vsb_level.set)  
            self.hsb_level = ttk.Scrollbar(self.label_frame_level, orient="horizontal", command=self.canvas_level.xview)
            self.canvas_level.configure(xscrollcommand=self.hsb_level.set)     
            
            self.vsb_level.pack(side="right", fill="y")
            self.hsb_level.pack(side="bottom", fill="x")
            self.canvas_level.pack(side = LEFT, fill = BOTH, expand = 1)
            self.canvas_level.create_window((0,0), window=self.frame_level, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_level.bind("<Configure>", lambda event, canvas=self.canvas_level: OnFrameConfigure(canvas))
            self.label_frame_level.place(relx = 0.05, rely = 0.6, relheight = 0.2, relwidth = 0.34, anchor = tk.NW)
            
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            self.label = ttk.Label(self.frame_level, text="Add custom variable(s) to:")
            self.label.grid(row=0, column=0, padx = 5, pady = 5, sticky=W)
            # Subject level
            self.level_CV = tk.StringVar()
            self.SubjectCV = ttk.Radiobutton(self.frame_level, text="Subjects", variable = self.level_CV, 
                                                           value = "Subjects", style="Popup.TRadiobutton")   
            self.SubjectCV.grid(row=1, column=0, padx = 5, pady = 5, sticky=W)
            # Session level     
            self.SessionCV = ttk.Radiobutton(self.frame_level, text="Sessions", variable = self.level_CV, 
                                                           value = "Sessions", state='disabled', style="Popup.TRadiobutton")   
            self.SessionCV.grid(row=2, column=0, padx = 5, pady = 5, sticky=W)
            
            self.level_CV.set("Subjects")
            self.SubjectCV.config(state=DISABLED)
            #####################################################################
            # Custom Variables (CV)
            textCV = "Custom Variables" 
            self.label_frame_CV = ttk.LabelFrame(self.frame_metadata, text=textCV , padding = 5, bootstyle="primary")
            
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
            self.label_frame_CV.place(relx = 0.5, rely = 0.60, relheight=0.2, relwidth=0.43, anchor = tk.NW)
            
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
            OPTIONS2 = ["g/kg"]
            self.selected_dose = tk.StringVar()
            self.dose_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_dose, width=10)
            self.dose_menu['values'] = OPTIONS2
            self.dose_menu['state'] = 'disabled'
            self.dose_menu.grid(row=2, column=2, padx = 5, pady = 5, sticky=W)
            
            self.sep1 = ttk.Separator(self.frame_level, bootstyle="primary")
            self.sep1.grid(row=3, column=0, padx = 5, pady = 5, sticky=EW)
            self.lab1 = ttk.Label(self.frame_level, text='Actions:', bootstyle="primary")
            self.lab1.grid(row=3, column=1, padx = 5, pady = 5, sticky=N)
            self.sep2 = ttk.Separator(self.frame_level, bootstyle="primary")
            self.sep2.grid(row=3, column=2, padx = 5, pady = 5, sticky=EW)


            #################### Modify the metadata ####################
            self.modify_btn = ttk.Button(self.frame_level, text="Modify", command = lambda: self.modify_metadata(), cursor=CURSOR_HAND, takefocus = 0, state = tk.DISABLED, style = "Secondary1.TButton")
            #self.modify_btn.place(relx=0.39, rely=0.60, anchor=tk.NE, relwidth=0.22)
            self.modify_btn.config(width = 13)
            self.modify_btn.grid(row=4, column=0, padx = 5, pady = 5, sticky=NSEW)
            Hovertip(self.modify_btn, "Edit the custom variables")
            #################### Confirm the metadata ####################
            self.confirm_btn = ttk.Button(self.frame_level, text="Confirm", command = lambda: self.confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0, state = tk.DISABLED, style = "Secondary1.TButton")
            #self.confirm_btn.place(relx=0.39, rely=0.70, anchor=tk.NE, relwidth=0.22)
            self.confirm_btn.config(width = 13)
            self.confirm_btn.grid(row=4, column=1, padx = 5, pady = 5, sticky=NSEW)
            Hovertip(self.modify_btn, "Confirm the custom variables for the selected subject/experiment")
            #################### Confirm multiple metadata ####################
            self.multiple_confirm_btn = ttk.Button(self.frame_level, text="Confirm +", command = lambda: self.confirm_multiple_metadata(master), cursor=CURSOR_HAND, takefocus = 0, state = tk.DISABLED, style = "Secondary1.TButton")
            #self.multiple_confirm_btn.place(relx=0.39, rely=0.80, anchor=tk.NE, relwidth=0.22)
            self.multiple_confirm_btn.config(width = 13)
            self.multiple_confirm_btn.grid(row=4, column=2, padx = 5, pady = 5, sticky=NSEW)
            Hovertip(self.modify_btn, "Confirm custom variables for multiple subjects/experiments")
            #################### Back button ####################
            self.back_btn = ttk.Button(self.frame_metadata, text="Back", command = lambda: self.back_action(master), cursor=CURSOR_HAND, takefocus = 0, state = tk.DISABLED, style = "Secondary1.TButton")
            self.back_btn.place(relx = 0.05, rely = 0.90, relwidth = 0.15, anchor = tk.NW)
        
        def back_action(self, master):
            try:
                destroy_widgets([self.frame_metadata, self.menu])
                self.overall_projectdata(master)
            except Exception as e:
                messagebox.showerror("XNAT-PIC", 'Error:' + str(e))
                raise

        def select_button(self, master, press_btn):
            disable_buttons([self.prj_data_btn, self.sbj_data_btn, self.exp_data_btn])
            # Choose your directory (button and menu)
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select " + press_btn + " directory!")
            if not self.information_folder:
                enable_buttons([self.prj_data_btn, self.sbj_data_btn, self.exp_data_btn])
                return
            enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SubjectCV, self.SessionCV, self.back_btn])
            # Read the data
            if press_btn == "Project":
                # Check if the selected folder is related to the right conversion flag
                if glob(self.information_folder + "/**/**/**/**/*.dcm", recursive=False) == [] and glob(self.information_folder + "/**/**/**/**/**/2dseq", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Project Data", "The selected folder is not project related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_metadata])
                    self.overall_projectdata(master)
                    return
                self.project_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 0)
                self.selection = 'Selected Project: ' + self.project_name
            elif press_btn == "Subject":
                # Check if the selected folder is related to the right conversion flag
                if glob(self.information_folder + "/**/**/**/*.dcm", recursive=False) == [] and glob(self.information_folder + "/**/**/**/**/2dseq", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Project Data", "The selected folder is not subject related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_metadata])
                    self.overall_projectdata(master)
                    return
                self.subject_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 1)
                self.selection = 'Selected Subject: ' + self.subject_name
            elif press_btn == "Experiment":
                # Check if the selected folder is related to the right conversion flag
                if glob(self.information_folder + "/**/**/*.dcm", recursive=False) == [] and glob(self.information_folder + "/**/**/**/2dseq", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Project Data", "The selected folder is not experiment related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_metadata])
                    self.overall_projectdata(master)
                    return
                self.experiment_name = (self.information_folder.rsplit("/",1)[1])
                params = metadata_params(self.information_folder, value = 2)
                self.selection = 'Selected Experiment: ' + self.experiment_name
            self.results_dict = params[0]
            self.todos = params[1]
            self.path_list = params[2]
            self.path_list1 = params[3]

            frame_notebook = []
            self.listbox_notebook = []
            for key in sorted(self.todos, key=len):
                frame_notebook.append(tk.Frame(self.notebook))
                frame_notebook[-1].pack()
                self.notebook.add(frame_notebook[-1], text=key, underline=0, sticky=tk.NE + tk.SW)
                self.listbox_notebook.append(tk.Listbox(frame_notebook[-1], selectbackground = AZURE, relief=tk.FLAT, font=SMALL_FONT_3, takefocus = 0))
                self.listbox_notebook[-1].insert(tk.END, *self.todos[key])
                self.listbox_notebook[-1].config(state=DISABLED)
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
            self.load_info(master)

            def change_frame(*args):
                # Normal entry CV
                for i in range(0, len(self.entries_value_CV)):
                    self.entries_value_CV[i]['state'] = 'normal'
                    self.entries_value_CV[i].delete(0, tk.END)
                    self.entries_value_CV[i]['state'] = 'disabled'
                # Clear all the combobox and the entry
                self.selected_group.set('')
                self.selected_timepoint.set('')
                self.selected_timepoint1.set('')
                self.time_entry.delete(0, tk.END)
                self.selected_dose.set('')     
                disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu])              
                if str(self.level_CV.get()) == "Subjects":
                    # Notebook
                    for i in range(len(self.listbox_notebook)):
                        self.listbox_notebook[i].config(state=DISABLED)
                    # Entries
                    if len(self.entries_variable_ID) > 2:
                        for i in range(2, len(self.entries_variable_ID)):
                            self.entries_variable_ID[i].destroy() 
                            self.entries_value_ID[i].destroy() 
                        del self.entries_variable_ID[2 : len(self.entries_variable_ID)]
                        del self.entries_value_ID[2 : len(self.entries_value_ID)]
                        self.cal.destroy()
                        del self.cal
                elif str(self.level_CV.get()) == "Sessions":
                    # Notebook
                    for i in range(len(self.listbox_notebook)):
                        self.listbox_notebook[i].config(state=NORMAL)
                    # Entries
                    if len(self.entries_variable_ID) == 2:
                        keys_ID = ["Experiment", "Acquisition_Date"]
                        # Entry ID         
                        count = 3
                        for key in keys_ID:
                            # Variable
                            self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
                            self.entries_variable_ID[-1].insert(0, key)
                            self.entries_variable_ID[-1]['state'] = 'disabled'
                            self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                            self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width= 20 if key == "Acquisition_Date" else 44))
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
                
                #################################################################
                # Load subject custom variables when switching from session to subject
                try: 
                    self.notebook.notebookContent.select(self.notebook.notebookTab.index("current"))
                except Exception as e:
                    pass
                # Events for the Subjects
                if str(self.level_CV.get()) == "Subjects":
                    # Clear all the combobox and the entry
                    self.selected_group.set('')
                    self.selected_timepoint.set('')
                    self.selected_timepoint1.set('')
                    self.time_entry.delete(0, tk.END)
                    self.selected_dose.set('')

                    disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu])
                    
                    # Find the tab
                    self.index_tab = self.notebook.notebookTab.index("current")
                    self.tab_name =  self.notebook.notebookTab.tab(self.index_tab, "text")
                    self.my_listbox = self.listbox_notebook[self.index_tab]
                    
                    def find_selected_folder():
                        for k,v in self.path_list1.items():
                            if str(self.tab_name) in str(k):
                                path = v.split('/')
                                sub_name = path[len(path)-2]
                                if sub_name == str(self.tab_name):
                                        self.selected_folder = k
                                        return
                    find_selected_folder()
                    tmp_dict = self.results_dict[self.selected_folder]

                    # Split the dictionary into ID and CV
                    complete_list = [list(group) for key, group in itertools.groupby(tmp_dict, lambda x: x == "SubjectsCV" or x == "SessionsCV") if not key]
                    dict_ID = {'Folder' : self.selected_folder}
                    dict_ID.update({k: v for k, v in tmp_dict.items() if k in complete_list[0]})
                    if str(self.level_CV.get()) == "Subjects":
                        dict_CV =  {k: v for k, v in tmp_dict.items() if k in complete_list[1]}
                    elif str(self.level_CV.get()) == "Sessions":
                        dict_CV =  {k: v for k, v in tmp_dict.items() if k in complete_list[2]} 
                    #################################################################                   
                    # ID: Modify the values ​​of the entries with the values ​​of the selected experiment
                    ind = 0
                    for key, value in dict_ID.items():
                        if ind==1 or ind==2:
                            # Variable ID
                            self.entries_variable_ID[ind-1]['state'] = 'normal'
                            self.entries_variable_ID[ind-1].delete(0, tk.END)
                            self.entries_variable_ID[ind-1].insert(0, key)
                            self.entries_variable_ID[ind-1]['state'] = 'disabled'
                            # Value ID
                            self.entries_value_ID[ind-1]['state'] = 'normal'
                            self.entries_value_ID[ind-1].delete(0, tk.END)
                            self.entries_value_ID[ind-1].insert(0, value if value is not None else '')
                            self.entries_value_ID[ind-1]['state'] = 'disabled'
                        ind += 1   
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
                        # Variable CV
                        if str(self.level_CV.get()) == "Subjects":
                            key1 = str(key).replace('Subjects', '')
                        elif str(self.level_CV.get()) == "Sessions":
                            key1 = str(key).replace('Sessions', '')
                        self.entries_variable_CV[ind]['state'] = 'normal'
                        self.entries_variable_CV[ind].delete(0, tk.END)
                        self.entries_variable_CV[ind].insert(0, key1)
                        self.entries_variable_CV[ind]['state'] = 'disabled'
                        # Value CV
                        self.entries_value_CV[ind]['state'] = 'normal'
                        self.entries_value_CV[ind].delete(0, tk.END)
                        self.entries_value_CV[ind].insert(0, value if value is not None else '')
                        self.entries_value_CV[ind]['state'] = 'disabled'
                        ind += 1
                elif str(self.level_CV.get()) == "Session":
                    return
                

            self.level_CV.trace('w', change_frame)
         #################### Load the info about the selected subject ####################
        def load_info(self, master):
            # Find the initial tab
            self.index_tab = self.notebook.notebookTab.index("current")
            self.tab_name = self.notebook.notebookTab.tab(self.index_tab, "text")
            self.my_listbox = self.listbox_notebook[self.index_tab]
            self.selected_index = None
            self.selected_folder = None

            def items_selected_subjects(event):
                try: 
                    self.notebook.notebookContent.select(self.notebook.notebookTab.index("current"))
                except Exception as e:
                    pass
                # Events for the Subjects
                if str(self.level_CV.get()) == "Subjects":
                    # Clear all the combobox and the entry
                    self.selected_group.set('')
                    self.selected_timepoint.set('')
                    self.selected_timepoint1.set('')
                    self.time_entry.delete(0, tk.END)
                    self.selected_dose.set('')

                    disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu])
                    
                    # Find the tab
                    self.index_tab = self.notebook.notebookTab.index("current")
                    self.tab_name =  self.notebook.notebookTab.tab(self.index_tab, "text")
                    self.my_listbox = self.listbox_notebook[self.index_tab]
                    
                    def find_selected_folder():
                        for k,v in self.path_list1.items():
                            if str(self.tab_name) in str(k):
                                path = v.split('/')
                                sub_name = path[len(path)-2]
                                if sub_name == str(self.tab_name):
                                        self.selected_folder = k
                                        return
                    find_selected_folder()
                    tmp_dict = self.results_dict[self.selected_folder]

                    # Split the dictionary into ID and CV
                    substring1 = 'Subjects'
                    substring2 = 'Sessions'

                    group_sub = {}
                    group_ses = {}
                    group_ID = {'Folder' : self.selected_folder}

                    for key, value in tmp_dict.items():
                        if substring1 in key and str(key) != 'SubjectsCV':
                            group_sub[key] = value
                        elif substring2 in key and str(key) != 'SessionsCV':
                            group_ses[key] = value
                        elif str(key) != 'SubjectsCV' and str(key) != 'SessionsCV':
                            group_ID[key] = value

                    dict_ID = group_ID
                    if str(self.level_CV.get()) == "Subjects":
                        dict_CV =  group_sub
                    elif str(self.level_CV.get()) == "Sessions":
                        dict_CV =  group_ses
                    
                    #################################################################                   
                    # ID: Modify the values ​​of the entries with the values ​​of the selected experiment
                    ind = 0
                    for key, value in dict_ID.items():
                        if ind==1 or ind==2:
                            # Variable ID
                            self.entries_variable_ID[ind-1]['state'] = 'normal'
                            self.entries_variable_ID[ind-1].delete(0, tk.END)
                            self.entries_variable_ID[ind-1].insert(0, key)
                            self.entries_variable_ID[ind-1]['state'] = 'disabled'
                            # Value ID
                            self.entries_value_ID[ind-1]['state'] = 'normal'
                            self.entries_value_ID[ind-1].delete(0, tk.END)
                            self.entries_value_ID[ind-1].insert(0, value if value is not None else '')
                            self.entries_value_ID[ind-1]['state'] = 'disabled'
                        ind += 1   

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
                        # Variable CV
                        if str(self.level_CV.get()) == "Subjects":
                            key1 = str(key).replace('Subjects', '')
                        elif str(self.level_CV.get()) == "Sessions":
                            key1 = str(key).replace('Sessions', '')
                        self.entries_variable_CV[ind]['state'] = 'normal'
                        self.entries_variable_CV[ind].delete(0, tk.END)
                        self.entries_variable_CV[ind].insert(0, key1)
                        self.entries_variable_CV[ind]['state'] = 'disabled'
                        # Value CV
                        self.entries_value_CV[ind]['state'] = 'normal'
                        self.entries_value_CV[ind].delete(0, tk.END)
                        self.entries_value_CV[ind].insert(0, value if value is not None else '')
                        self.entries_value_CV[ind]['state'] = 'disabled'
                        ind += 1
                elif str(self.level_CV.get()) == "Session":
                    return
            # Add the event: change Tab  
            self.notebook.notebookTab.bind("<<NotebookTabChanged>>", items_selected_subjects)
            
            def items_selected_sessions(event):
                # Events for the Sessions
                if str(self.level_CV.get()) == "Sessions":
                    # Clear all the combobox and the entry
                    self.selected_group.set('')
                    self.selected_timepoint.set('')
                    self.selected_timepoint1.set('')
                    self.time_entry.delete(0, tk.END)
                    self.selected_dose.set('')

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
                    substring1 = 'Subjects'
                    substring2 = 'Sessions'

                    group_sub = {}
                    group_ses = {}
                    group_ID = {'Folder' : self.selected_folder}

                    for key, value in tmp_dict.items():
                        if substring1 in key and str(key) != 'SubjectsCV':
                            group_sub[key] = value
                        elif substring2 in key and str(key) != 'SessionsCV':
                            group_ses[key] = value
                        elif str(key) != 'SubjectsCV' and str(key) != 'SessionsCV':
                            group_ID[key] = value

                    dict_ID = group_ID
                    if str(self.level_CV.get()) == "Subjects":
                        dict_CV =   group_sub
                    elif str(self.level_CV.get()) == "Sessions":
                        dict_CV =  group_ses
                    
                    #################################################################
                    # Modify the values ​​of the entries with the values ​​of the selected experiment
                    ind = 0
                    for key, value in dict_ID.items():
                        if ind > 0:
                            # Variable ID
                            self.entries_variable_ID[ind-1]['state'] = 'normal'
                            self.entries_variable_ID[ind-1].delete(0, tk.END)
                            self.entries_variable_ID[ind-1].insert(0, key)
                            self.entries_variable_ID[ind-1]['state'] = 'disabled'
                            # Value ID
                            self.entries_value_ID[ind-1]['state'] = 'normal'
                            self.entries_value_ID[ind-1].delete(0, tk.END)
                            self.entries_value_ID[ind-1].insert(0, value if value is not None else '')
                            self.entries_value_ID[ind-1]['state'] = 'disabled'
                        ind += 1

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
                        # Variable CV
                        if str(self.level_CV.get()) == "Subjects":
                            key1 = str(key).replace('Subjects', '')
                        elif str(self.level_CV.get()) == "Sessions":
                            key1 = str(key).replace('Sessions', '')
                        self.entries_variable_CV[ind]['state'] = 'normal'
                        self.entries_variable_CV[ind].delete(0, tk.END)
                        self.entries_variable_CV[ind].insert(0, key1)
                        self.entries_variable_CV[ind]['state'] = 'disabled'
                        # Value CV
                        self.entries_value_CV[ind]['state'] = 'normal'
                        self.entries_value_CV[ind].delete(0, tk.END)
                        self.entries_value_CV[ind].insert(0, value if value is not None else '')
                        self.entries_value_CV[ind]['state'] = 'disabled'
                        ind += 1
                
            # Add the event to the list of listbox (press Tab)   
            for i in range(len(self.listbox_notebook)):
                self.listbox_notebook[i].bind('<Tab>', items_selected_sessions)
        # Modify Metadata
        def modify_metadata(self):
            # Check before editing the data
            if str(self.level_CV.get()) == "Sessions" and not self.entries_value_ID[3].get():
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return 
                       
            # Normal entry CV
            for i in range(0, len(self.entries_value_CV)):
                self.entries_value_CV[i]['state'] = 'normal'
          
            # The timepoint field remains locked. Only one value can be entered from the entry.
            self.entries_value_CV[1]['state'] = 'disabled'

            # Option menu for the group (treated/untreated)
            self.group_menu['state'] = 'readonly'
            def group_changed(event):
                """ handle the group changed event """
                self.entries_value_CV[0].delete(0, tk.END)
                self.entries_value_CV[0].insert(0, str(self.selected_group.get()))  
                if str(self.level_CV.get()) == "Sessions":                  
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
                        value_dose = dose.replace(' g/kg','')
                        float(value_dose)
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC", 'Insert a number in dose')
                        raise

                self.entries_value_CV[2].delete(0, tk.END)
                self.entries_value_CV[2].insert(0, str(value_dose) + ' ' + str(self.selected_dose.get()))    
                if str(self.level_CV.get()) == "Sessions":                
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
                
                if str(self.level_CV.get()) == "Sessions":
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

            if not self.entries_value_ID[0].get():
                raise Exception ("Insert the name of the project!")

            if not self.entries_value_ID[1].get():
                raise Exception ("Insert the name of the subject!")

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
                    dose_value = self.entries_value_CV[2].get().replace(' g/kg',"")
                    float(dose_value)
                except Exception as e: 
                    raise Exception ("Insert a number in dose")

        # Update the values and save the values in a txt file        
        def save_entries(self, my_key, multiple, sub_name):
            def savetxt(my_key):
                # Saves the changes made by the user in the txt file
                substring = self.path_list1.get(my_key)
                name_txt = str(my_key).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
                tmp_path = ''
                for dirpath, dirnames, filenames in os.walk(substring.replace('\\', '/')):
                # Check if the visu pars file is in the scans
                    for filename in [f for f in filenames if f.startswith("visu_pars")]:
                        tmp_path = substring + "\\" + name_txt
                        break
                    # Check if the DICOM is in the scans
                    for filename in [f for f in filenames if f.endswith(".dcm")]:
                        tmp_path = substring + "\\MR\\" + name_txt
                        break
                    if tmp_path:
                        break
                try:
                    with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                        meta_file.write(tabulate(self.results_dict[my_key].items(), headers=['Variable', 'Value']))
                except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
                        raise    

            if multiple == 0:
            # Single confirm
                array_CV = range(0, len(self.entries_variable_CV))
            elif multiple ==1:
            # Multple confirm
                array_CV = self.list_CV
                
            tmp_CV = {}
            
            if str(self.level_CV.get()) == "Subjects":
                # Update the info in the txt file CV
                for i in array_CV:
                    keyCV = "Subjects" + str(self.entries_variable_CV[i].get())
                    keyCV1 = "Sessions" + str(self.entries_variable_CV[i].get())
                    new_value_sub = self.entries_value_CV[i].get() 
                    new_value_sub = "" if new_value_sub is None else new_value_sub
                    tmp_CV.update({keyCV : new_value_sub, keyCV1 : new_value_sub})    
                    self.entries_variable_CV[i]['state'] = tk.DISABLED
                    self.entries_value_CV[i]['state'] = tk.DISABLED 
                # Find all the keys for the subject (Sub+Exp) that you want to update
                keys = []
                for k,v in self.path_list1.items():
                    if str(sub_name) in str(k):
                        path = v.split('/')
                        sub_name1 = path[len(path)-2]
                        if sub_name == str(sub_name1):
                            keys.append(k)
                for x in range(len(keys)):
                    my_key = keys[x]           
                    self.results_dict[my_key].update(tmp_CV)
                    savetxt(my_key)
            elif str(self.level_CV.get()) == "Sessions":
                # Update the info in the txt file CV
                for i in array_CV:
                    keyCV = "Sessions" + str(self.entries_variable_CV[i].get())
                    new_value_ses = self.entries_value_CV[i].get() 
                    tmp_CV.update({keyCV : new_value_ses})     
                    self.entries_variable_CV[i]['state'] = tk.DISABLED
                    self.entries_value_CV[i]['state'] = tk.DISABLED 
         
                self.results_dict[my_key].update(tmp_CV)
                savetxt(my_key)
           
            # Clear all 
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            self.selected_dose.set('')
            disable_buttons([self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.dose_menu])            

        def confirm_metadata(self):
            # Check before editing the data
            if str(self.level_CV.get()) == "Sessions" and not self.entries_value_ID[2].get():
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return 

            try:
                self.check_entries()
            except Exception as e: 
                messagebox.showerror("XNAT-PIC", "Error in checking fields: " + str(e))  
                raise

            try:
                self.save_entries(self.selected_folder, multiple=0, sub_name = self.tab_name)
            except Exception as e: 
                messagebox.showerror("XNAT-PIC", "Error in saving: " + str(e))  
                raise  
        ##################### Confirm multiple metadata ####################
        def confirm_multiple_metadata(self, master):

            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
            
            for i in range(len(self.entries_variable_CV)):  
                self.entries_variable_CV[i]['state'] = tk.DISABLED
                self.entries_value_CV[i]['state'] = tk.DISABLED    

            # Clear all 
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            self.selected_dose.set('')

            # Check before editing the data
            if str(self.level_CV.get()) == "Sessions" and not self.entries_value_ID[3].get():
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                return 
            self.select_CV(master)

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
                    if str(self.level_CV.get()) == "Sessions":
                        self.select_exp(master)
                    if str(self.level_CV.get()) == "Subjects":
                        self.select_sub(master)

            # Delete ID
            def multiple_delete_CV(row):
                btn_multiple_confirm_CV[row].destroy()
                btn_multiple_delete_CV[row].destroy()
                count_list.pop()
                # If the user has finished all the selections of the CV, he moves on to the selection of experiments
                if len(count_list) == 0:
                    if str(self.level_CV.get()) == "Sessions":
                        self.select_exp(master)
                    if str(self.level_CV.get()) == "Subjects":
                        self.select_sub(master)

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
                            self.save_entries(self.list_tab_listbox[x][y], multiple=1, sub_name=self.tab_name)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Error in saving" + str(e))  
                            raise
                
                # Clear all 
                self.selected_group.set('')
                self.selected_dose.set('')
                self.selected_timepoint.set('')
                self.selected_timepoint1.set('')
                self.time_entry.delete(0, tk.END)
                disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1])
                # Clear the focus and the select mode of the listbox is single
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                self.my_listbox.selection_clear(0, 'end')
                for i in range(len(self.listbox_notebook)):
                    self.listbox_notebook[i]['selectmode'] = SINGLE 
                    self.listbox_notebook[i]['exportselection']= TRUE  
                self.load_info(master)

            self.ok_btn = ttk.Button(self.frame_metadata, image = master.logo_accept, command = items_selected2, cursor=CURSOR_HAND)
            self.ok_btn.place(relx = 0.18, rely = 0.53, anchor = NW)
            
            # The user presses cancel
            def items_cancel():
                self.no_btn.destroy()
                self.ok_btn.destroy()
                # Clear the focus and the select mode of the listbox is single
                messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                for i in range(len(self.listbox_notebook)):
                    self.listbox_notebook[i]['selectmode'] = SINGLE 
                    self.listbox_notebook[i]['exportselection']= TRUE 
            self.no_btn = ttk.Button(self.frame_metadata, image = master.logo_delete, command = items_cancel, cursor=CURSOR_HAND)
            self.no_btn.place(relx = 0.26, rely = 0.53, anchor = NE)
        def select_sub(self, master):
            # Popup
            self.popup_subject = ttk.Toplevel()
            self.popup_subject.title("XNAT-PIC ~ Project Data")
            master.root.eval(f'tk::PlaceWindow {str(self.popup_subject)} center')
            self.popup_subject.resizable(False, False)
            self.popup_subject.grab_set()
            
            # If you want the logo 
            self.popup_subject.iconbitmap(PATH_IMAGE + "logo3.ico")

            # Select the subjects to copy the custom variables to
            self.popup_subject_frame = ttk.LabelFrame(self.popup_subject, text="Custom Variables", style="Popup.TLabelframe")
            self.popup_subject_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)
            self.canvas_sub = tk.Canvas(self.popup_subject_frame)
            self.frame_sub = tk.Frame(self.canvas_sub)

            # Scrollbar
            self.vsb_sub = ttk.Scrollbar(self.popup_subject_frame, orient="vertical", command=self.canvas_sub.yview)
            self.canvas_sub.configure(yscrollcommand=self.vsb_sub.set)  
            self.hsb_sub = ttk.Scrollbar(self.popup_subject_frame, orient="horizontal", command=self.canvas_sub.xview)
            self.canvas_sub.configure(xscrollcommand=self.hsb_sub.set)

            self.vsb_sub.pack(side="right", fill="y")     
            self.hsb_sub.pack(side="bottom", fill="x")
            self.canvas_sub.pack(side = LEFT, fill = BOTH, expand = 1)
            self.canvas_sub.create_window((0,0), window=self.frame_sub, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_sub.bind("<Configure>", lambda event, canvas=self.canvas_sub: OnFrameConfigure(canvas))

            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))
            # Label     
            self.popup_subject.label = ttk.Label(self.frame_sub, text="Select the subjects to copy the custom variables to:")  
            self.popup_subject.label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

            # List of subjects
            self.subjects = []        
            count = 2
            self.sub_flag = []
            for key in self.todos:
                # Variable
                self.sub_flag.append(BooleanVar(value=False))
                ttk.Checkbutton(self.frame_sub, variable=self.sub_flag[count-2], 
                                text=key, cursor=CURSOR_HAND).grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                if str(key) == self.tab_name:
                    self.sub_flag[-1].set(True)
                    ttk.Checkbutton(self.frame_sub, variable=self.sub_flag[count-2], 
                                text=key, state=tk.DISABLED,cursor=CURSOR_HAND).grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                    
                count += 1

            def save_prj():
                try:
                    self.popup_subject.destroy()
                except:
                    pass
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                for text, var in zip(self.todos, self.sub_flag):
                    if var.get():
                        try:
                            self.save_entries(self.selected_folder, multiple=0, sub_name = text)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Error in saving" + str(e))  
                            raise

            self.popup_subject.button_ok = ttk.Button(self.popup_subject, image = master.logo_accept,
                                                command = save_prj , cursor=CURSOR_HAND)
            self.popup_subject.button_ok.grid(row=2, column=1, padx=10, pady=5, sticky=NW)
            
            # If the popup is closed, it re-enables the buttons
            def enable():
                try:
                    self.popup_subject.destroy()
                except:
                    pass
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
               
            self.popup_subject.button_cancel = ttk.Button(self.popup_subject, image = master.logo_delete,
                                                command = enable, cursor=CURSOR_HAND)
            self.popup_subject.button_cancel.grid(row=2, column=0, padx=10, pady=5, sticky=NE)

            self.popup_subject.protocol('WM_DELETE_WINDOW', enable)
             
        ##################### Modify ID Name ########################
        def modify_ID_metadata(self, master, flag_ID):
            # Check before editing the data
            if not self.entries_value_ID[0].get():
                messagebox.showerror("XNAT-PIC", "Select a folder")
                return 
            # Normal entry CV
            for i in range(0, len(self.entries_value_CV)):
                self.entries_value_CV[i]['state'] = 'disabled'
        
            # Clear all 
            self.selected_group.set('')
            self.selected_dose.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1])
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])

            if flag_ID == "Project":               
                # Modify Project Name
                self.entries_value_ID[0]['state'] = 'normal'
                self.project_name = self.entries_value_ID[0].get()
                self.subject_name = self.entries_value_ID[1].get()
                def confirm_project_name():
                    new_prj = self.entries_value_ID[0].get()
                    if not new_prj:
                        messagebox.showerror("XNAT-PIC", "Insert the name of the project!")
                        return
                    self.entries_value_ID[0]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    for k,v in self.results_dict.items():
                        self.results_dict[k]['Project'] = new_prj
                    for k,v in self.path_list1.items():
                        # Saves the changes made by the user in the txt file
                        substring = v
                        name_txt = str(k).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
                        tmp_path = ''
                        for dirpath, dirnames, filenames in os.walk(substring.replace('\\', '/')):
                        # Check if the visu pars file is in the scans
                            for filename in [f for f in filenames if f.startswith("visu_pars")]:
                                tmp_path = substring + "\\" + name_txt
                                break
                            # Check if the DICOM is in the scans
                            for filename in [f for f in filenames if f.endswith(".dcm")]:
                                tmp_path = substring + "\\MR\\" + name_txt
                                break
                            if tmp_path:
                                break
                        try:
                            with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                                meta_file.write(tabulate(self.results_dict[k].items(), headers=['Variable', 'Value']))
                        except Exception as e: 
                                messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
                                raise    
                    btn_project_delete_ID.destroy()        
                    btn_project_confirm_ID.destroy()
                    
                btn_project_confirm_ID = ttk.Button(self.frame_metadata, image = master.logo_accept, 
                                                command=confirm_project_name, cursor=CURSOR_HAND)
                btn_project_confirm_ID.place(relx = 0.65, rely = 0.53, anchor = NE)

                def delete_project_name():
                    self.entries_value_ID[0].delete(0, tk.END)
                    self.entries_value_ID[0].insert(0, self.project_name)
                    self.entries_value_ID[0]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    btn_project_delete_ID.destroy()
                    btn_project_confirm_ID.destroy()

                btn_project_delete_ID = ttk.Button(self.frame_metadata, image = master.logo_delete, 
                                                command=delete_project_name, cursor=CURSOR_HAND)
                btn_project_delete_ID.place(relx = 0.71, rely = 0.53, anchor = NE)

            elif flag_ID == "Subject":
                # Modify Project Name
                self.entries_value_ID[1]['state'] = 'normal'
                
                def confirm_subject_name():
                    new_sub = self.entries_value_ID[1].get()
                    if not new_sub:
                        messagebox.showerror("XNAT-PIC", "Insert the name of the subject!")
                        return 
                    self.entries_value_ID[1]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    
                    keys = []
                    for k,v in self.path_list1.items():
                        if str(self.tab_name) in str(k):
                            path = v.split('/')
                            sub_name = path[len(path)-2]
                            if sub_name == str(self.tab_name):
                                self.results_dict[k]['Subject'] = new_sub
                                keys.append(k)
                    for x in range(len(keys)):
                        my_key = keys[x]           
                        substring = self.path_list1.get(my_key)
                        name_txt = str(my_key).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
                        tmp_path = ''
                        for dirpath, dirnames, filenames in os.walk(substring.replace('\\', '/')):
                        # Check if the visu pars file is in the scans
                            for filename in [f for f in filenames if f.startswith("visu_pars")]:
                                tmp_path = substring + "\\" + name_txt
                                break
                            # Check if the DICOM is in the scans
                            for filename in [f for f in filenames if f.endswith(".dcm")]:
                                tmp_path = substring + "\\MR\\" + name_txt
                                break
                            if tmp_path:
                                break
                        try:
                            with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                                meta_file.write(tabulate(self.results_dict[my_key].items(), headers=['Variable', 'Value']))
                        except Exception as e: 
                                messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
                                raise    

                    btn_subject_delete_ID.destroy()        
                    btn_subject_confirm_ID.destroy()
                    
                btn_subject_confirm_ID = ttk.Button(self.frame_metadata, image = master.logo_accept, 
                                                command=confirm_subject_name, cursor=CURSOR_HAND)
                btn_subject_confirm_ID.place(relx = 0.65, rely = 0.53, anchor = NE)

                def delete_subject_name():
                    self.entries_value_ID[1].delete(0, tk.END)
                    self.entries_value_ID[1].insert(0, self.subject_name)
                    self.entries_value_ID[1]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    btn_subject_delete_ID.destroy()
                    btn_subject_confirm_ID.destroy()

                btn_subject_delete_ID = ttk.Button(self.frame_metadata, image = master.logo_delete, 
                                                command=delete_subject_name, cursor=CURSOR_HAND)
                btn_subject_delete_ID.place(relx = 0.71, rely = 0.53, anchor = NE)

            elif flag_ID == "Experiment":
                if str(self.level_CV.get()) == "Subjects":
                    messagebox.showerror("XNAT-PIC", "Select Sessions Level")
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    return 
                if str(self.level_CV.get()) == "Sessions" and not self.entries_value_ID[2].get():
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    return 
                # Modify Project Name
                self.entries_value_ID[2]['state'] = 'normal'
                self.experiment_name = self.entries_value_ID[2].get()
                def confirm_exp_name():
                    new_exp = self.entries_value_ID[2].get()
                    if not new_exp:
                        messagebox.showerror("XNAT-PIC", "Insert the name of the experiment!")
                        return 
                    self.entries_value_ID[2]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
 
                    self.results_dict[self.selected_folder]['Experiment'] = new_exp
                    self.confirm_metadata()

                    btn_exp_delete_ID.destroy()        
                    btn_exp_confirm_ID.destroy()
                    
                btn_exp_confirm_ID = ttk.Button(self.frame_metadata, image = master.logo_accept, 
                                                command=confirm_exp_name, cursor=CURSOR_HAND)
                btn_exp_confirm_ID.place(relx = 0.65, rely = 0.53, anchor = NE)

                def delete_exp_name():
                    self.entries_value_ID[2].delete(0, tk.END)
                    self.entries_value_ID[2].insert(0, self.experiment_name)
                    self.entries_value_ID[2]['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    btn_exp_delete_ID.destroy()
                    btn_exp_confirm_ID.destroy()

                btn_exp_delete_ID = ttk.Button(self.frame_metadata, image = master.logo_delete, 
                                                command=delete_exp_name, cursor=CURSOR_HAND)
                btn_exp_delete_ID.place(relx = 0.71, rely = 0.53, anchor = NE)

            elif flag_ID == "Acquisition Date":
                if str(self.level_CV.get()) == "Subjects":
                    messagebox.showerror("XNAT-PIC", "Select Sessions Level")
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    return 
                if str(self.level_CV.get()) == "Sessions" and not self.entries_value_ID[2].get():
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    return 

                # Modify acq date Name
                self.cal.entry['state'] = 'normal'
                self.cal.button['state'] = 'normal'
                self.flag = 0
                self.entries_value_ID[3]['state'] = 'normal'
                self.acquisition_date_name = self.entries_value_ID[3].get()

                            # # Acquisition date: you can modify date with the calendar           
                def date_entry_selected(*args):
                    if self.flag == 0:
                        self.entries_value_ID[3]['state'] = tk.NORMAL
                        self.entries_value_ID[3].delete(0, tk.END)
                        self.entries_value_ID[3].insert(0, str(self.cal.entry.get()))
                        if self.entries_value_ID[3].get():
                            try:
                                acq_date = dt.datetime.strptime(self.entries_value_ID[3].get(), '%Y-%m-%d')
                                self.today = date.today()
                                self.today = self.today.strftime('%Y-%m-%d')
                                if acq_date.strftime('%Y-%m-%d') > self.today:
                                    self.entries_value_ID[3].delete(0, tk.END)
                                    raise Exception("The date entered is greater than today's date")
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC", str(e))
                                self.entries_value_ID[3].delete(0, tk.END)
                                self.entries_value_ID[3]['state'] = tk.DISABLED
                                raise

                        self.entries_value_ID[3]['state'] = tk.DISABLED
                        self.my_listbox.selection_set(self.selected_index)
            
                self.datevar.trace('w', date_entry_selected)

                def confirm_date_name():
                    self.flag = 1
                    self.cal.entry.delete(0, tk.END)
                    self.cal.entry['state'] = 'disabled'
                    self.cal.button['state'] = 'disabled'
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    
                    new_date = self.entries_value_ID[3].get()

                    self.results_dict[self.selected_folder]['Acquisition_date'] = new_date
                    self.confirm_metadata()

                    btn_date_delete_ID.destroy()        
                    btn_date_confirm_ID.destroy()
                    
                btn_date_confirm_ID = ttk.Button(self.frame_metadata, image = master.logo_accept, 
                                                command=confirm_date_name, cursor=CURSOR_HAND)
                btn_date_confirm_ID.place(relx = 0.65, rely = 0.53, anchor = NE)

                def delete_date_name():
                    self.flag = 1
                    self.entries_value_ID[3]['state'] = tk.NORMAL
                    self.cal.entry.delete(0, tk.END)
                    self.entries_value_ID[3].delete(0, tk.END)
                    self.entries_value_ID[3].insert(0, self.acquisition_date_name)
                    self.cal.entry['state'] = 'disabled'
                    self.cal.button['state'] = 'disabled'
                    self.entries_value_ID[3]['state'] = tk.DISABLED
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.SessionCV, self.SubjectCV])
                    btn_date_delete_ID.destroy()
                    btn_date_confirm_ID.destroy()

                btn_date_delete_ID = ttk.Button(self.frame_metadata, image = master.logo_delete, 
                                                command=delete_date_name, cursor=CURSOR_HAND)
                btn_date_delete_ID.place(relx = 0.71, rely = 0.53, anchor = NE)
        ##################### Clear the metadata ####################              
        def clear_metadata(self, flag):
            # Check before editing the data
            if not self.entries_value_ID[0].get():
                messagebox.showerror("XNAT-PIC", "Select a folder")
                return 
            # Clear all the combobox and the entry
            self.selected_dose.set('')
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            state = self.entries_value_ID[1]['state']
            if flag =='All':
                # Set empty string in all the entries
                for i in range(0, len(self.entries_variable_CV)):
                        self.entries_value_CV[i]['state'] = tk.NORMAL
                        self.entries_value_CV[i].delete(0, tk.END)
                        self.entries_value_CV[i]['state'] = state
            elif flag == 'Group':
                self.entries_value_CV[0]['state'] = tk.NORMAL
                self.entries_value_CV[0].delete(0, tk.END)
                self.entries_value_CV[0]['state'] = state
            elif flag == 'Timepoint':
                    self.entries_value_CV[1]['state'] = tk.NORMAL
                    self.entries_value_CV[1].delete(0, tk.END)
                    self.entries_value_CV[1]['state'] = state
            elif flag == 'Dose':
                    self.entries_value_CV[2]['state'] = tk.NORMAL
                    self.entries_value_CV[2].delete(0, tk.END)
                    self.entries_value_CV[2]['state'] = state
            self.confirm_metadata()

        ##################### Add Custom Variable #################
        def add_custom_variable(self, master):
            # Check before editing the data
            if not self.entries_value_ID[0].get():
                messagebox.showerror("XNAT-PIC", "Select a folder")
                return 
            # Disable btns
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
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
                    try:
                        self.save_entries(self.selected_folder, multiple=0, sub_name = self.tab_name)
                    except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Error in saving: " + str(e))  
                        raise  
                    state = self.entries_value_ID[1]['state']    
                    self.entries_variable_CV[next_row]['state'] = tk.DISABLED
                    self.entries_value_CV[next_row]['state'] = state
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
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
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                btn_confirm_CV.destroy()
                btn_reject_CV.destroy()
            btn_reject_CV = ttk.Button(self.frame_CV, image = master.logo_delete, 
                                            command=lambda: reject_CV(next_row), cursor=CURSOR_HAND)
            btn_reject_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NE)
        # #################### Save all the metadata ####################
        def save_metadata(self):
            # Check before editing the data
            if not self.entries_value_ID[0].get():
                messagebox.showerror("XNAT-PIC", "Select a folder")
                return 
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
            result = messagebox.askquestion("Exit", "Do you want to go back to home?", icon='warning')
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
                if self.upload_type.get() == 0 and glob(self.folder_to_upload.get() + "/**/**/**/**/*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not project related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return
                if self.upload_type.get() == 1 and glob(self.folder_to_upload.get() + "/**/**/**/*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not subject related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return
                if self.upload_type.get() == 2 and glob(self.folder_to_upload.get() + "/**/**/*.dcm", recursive=False) == []:
                    messagebox.showerror("XNAT-PIC Uploader", "The selected folder is not experiment related.\nPlease select an other directory!")
                    destroy_widgets([self.frame_uploader])
                    self.overall_uploader(master)
                    return

                # if (self.upload_type.get() == 1 or self.upload_type.get() == 2) and (glob(self.folder_to_upload.get() + "/**/**/**/*.dcm", recursive=False) == [] and
                #                                                                       glob(self.folder_to_upload.get() + "/**/**/*.dcm", recursive=False) == []):
                #     messagebox.showerror("XNAT-PIC Uploader", "The selected folder does not contain DICOM files!")
                #     destroy_widgets([self.frame_uploader])
                #     self.overall_uploader(master)
                #     return
                # Reset and clear the selected_item_path defined from Treeview widget selection
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
                        # Check if there are CV 
                        CV_exist_prj = glob(self.working_folder + '/**/**/**/*custom_variables.txt', recursive=False)
                        text_CV_prj = 'No' if CV_exist_prj == [] else 'Yes'
                        
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
                                    list_CV_sub = []
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
                                            CV_exist_exp =  glob(tmp_exp_path + '/**/*custom_variables.txt', recursive=False)
                                            text_CV_exp = 'No' if CV_exist_exp == [] else 'Yes'
                                            list_CV_sub.append(text_CV_exp)
                                            val_exp_1 = "Experiment"
                                        dict_items[str(j)] = {}
                                        dict_items[str(j)]['parent'] = '1'
                                        dict_items[str(j)]['text'] = sub2
                                        dict_items[str(j)]['values'] = (val_exp_1)
                                        j += 1

                                text_CV_exp = 'Yes' if all(x == 'Yes' for x in list_CV_sub) else 'No'
                                dict_items[str(branch_idx)]['values'] = ("Subject", text_CV_exp)

                        # Update the fields of the parent object
                        dict_items['0']['values'] = ("Project", text_CV_prj)
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
                            list_CV_sub = []
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
                                    list_CV_sub = []
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
                                                    CV_exist_exp =  glob(tmp_exp_path + '/**/*custom_variables.txt', recursive=False)
                                                    text_CV_exp = 'No' if CV_exist_exp == [] else 'Yes'
                                                    list_CV_sub.append(text_CV_exp)
                                                    dict_items[str(j)]['values'] = ("Experiment")
                                            elif self.upload_type.get() == 2:
                                                tmp_exp_path1 = os.path.join(self.working_folder, sub, sub2)
                                                if glob(tmp_exp_path1 + "/*.dcm", recursive=False) == []:
                                                    dict_items[str(j)]['values'] = ("Folder")
                                                else:
                                                    dict_items[str(j)]['values'] = ("Scan")
                                            j += 1
                                    if self.upload_type.get() == 0:    
                                        text_CV_exp = 'Yes' if all(x == 'Yes' for x in list_CV_sub) else 'No'
                                        dict_items[str(branch_idx)]['values'] = ("Subject", text_CV_exp)
                                        list_CV_sub = []
                                    elif self.upload_type.get() == 2:    
                                        dict_items[str(branch_idx)]['values'] = ("Imaging-Technique")

                            # Update the fields of the parent object
                            if self.upload_type.get() == 0:
                                CV_exist_prj = glob(self.working_folder + '/**/**/**/*custom_variables.txt', recursive=False)
                                text_CV_prj = 'No' if CV_exist_prj == [] else 'Yes'
                                dict_items['0']['values'] = ("Project", text_CV_prj)
                            if self.upload_type.get() == 2:
                                CV_exist = glob(self.working_folder + '/**/*custom_variables.txt', recursive=False)
                                text_CV = 'No' if CV_exist == [] else 'Yes'
                                dict_items['0']['values'] = ("Experiment", text_CV)
                            
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
                                list_CV_sub = []
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
                                        CV_exist_exp =  glob(tmp_exp_path + '/**/*custom_variables.txt', recursive=False)
                                        text_CV_exp = 'No' if CV_exist_exp == [] else 'Yes'
                                        list_CV_sub.append(text_CV_exp)
                                        val_exp = "Experiment"
                                    branch_idx = j
                                    dict_items[str(j)] = {}
                                    dict_items[str(j)]['parent'] = '0'
                                    dict_items[str(j)]['text'] = sub
                                    j += 1
                                        
                                    dict_items[str(branch_idx)]['values'] = (val_exp)

                            # Update the fields of the parent object
                            text_CV_exp = 'Yes' if all(x == 'Yes' for x in list_CV_sub) else 'No'
                            dict_items['0']['values'] = ("Subject", text_CV_exp)
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
                                list_CV_sub = []
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
            
            columns = [("#0", "Folder"), ("#1", "Type"), ("#2", "Custom Variables")]
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
                    #self.search_entry.config(state='disabled')
                    self.folder_to_upload.set("")

            # self.clear_tree_btn = ttk.Button(self.frame_uploader, image=master.logo_clear,
            #                         cursor=CURSOR_HAND, command=clear_tree, style="WithoutBack.TButton")
            # self.clear_tree_btn.place(relx = 0.47, rely = 0.25, anchor = NE)
            
            # See the entire project
            self.chkvar_entire_prj = tk.BooleanVar()
            self.chkvar_entire_prj.set(False)
            self.chkbtn_entire_prj = ttk.Checkbutton(self.frame_uploader, text="View the entire project", variable=self.chkvar_entire_prj, command=folder_selected_handler, state='disabled', bootstyle="round-toggle", cursor=CURSOR_HAND)
            self.chkbtn_entire_prj.place(relx = 0.29, rely = 0.25, anchor = NW)
            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = ttk.Checkbutton(self.frame_uploader, variable=self.add_file_flag, onvalue=1, offvalue=0, 
                                text="Additional Files", state='disabled', bootstyle="round-toggle", cursor=CURSOR_HAND)
            self.add_file_btn.place(relx = 0.53, rely = 0.25, anchor = NW)
            
            # Label Frame Uploader Custom Variables
            self.custom_var_labelframe = ttk.Labelframe(self.frame_uploader, text = 'Custom Variables')
            self.custom_var_labelframe.place(relx = 0.53, rely = 0.31, relheight=0.30, relwidth = 0.42, anchor = NW)
            
            # Custom Variables
            # self.n_custom_var = tk.IntVar()
            # self.n_custom_var.set(3)
            # custom_var_options = list(range(0, 4))
            # self.custom_var_list = ttk.OptionMenu(self.custom_var_labelframe, self.n_custom_var, 0, *custom_var_options)
            # self.custom_var_list.config(width=2, cursor=CURSOR_HAND)
            # self.custom_var_list.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
            my_string_var = StringVar()
            my_string_var.set("Custom Variables")
            self.custom_var_label = ttk.Label(self.custom_var_labelframe, textvariable=my_string_var, font = 'bold')
            self.custom_var_label.grid(row=0, column=1, padx=2, pady=5, sticky=tk.NW)

            # Show Custom Variables
            def display_custom_var(*args):
                for widget in self.custom_var_labelframe.winfo_children():
                    if widget.grid_info()['row'] > 0:
                        widget.destroy()

                if self.selected_item_path.get() != '':
                #if self.n_custom_var.get() != 0:
                    try:
                        if str(self.type_folder) == 'Subject':
                            my_string_var.set("Subject Level")
                            list_of_files = glob(self.selected_item_path.get() + '/**/**/*custom_variables.txt', recursive=False)
                            no_keys = ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'SubjectsCV', 'SessionsCV', 'SessionsGroup', 'SessionsTimepoint', 'SessionsDose', 'SessionsB0', 'SessionsMagneticField']
                        elif str(self.type_folder) == 'Experiment':
                            my_string_var.set("Experiment Level")
                            list_of_files = glob(self.selected_item_path.get() + '/**/*custom_variables.txt', recursive=False)
                            no_keys = ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'SubjectsCV', 'SessionsCV', 'SubjectsGroup', 'SubjectsTimepoint', 'SubjectsDose', 'SubjectsB0', 'SubjectsMagneticField']
                        else: 
                            my_string_var.set("Custom Variables")
                            return
                        custom_file = [x for x in list_of_files if 'Custom' in x]
                        custom_variables = read_table(custom_file[0])
                        info = {}
                        custom_vars = [(key, custom_variables[key]) for key in custom_variables.keys() 
                                            if key not in no_keys]
                    except:
                        info = {"Project": self.selected_item_path.get().split('/')[-3], 
                                "Subject": self.selected_item_path.get().split('/')[-2], 
                                "Experiment": self.selected_item_path.get().split('/')[-1], 
                                "Acquisition_date": "", 
                                "SubjectsCV": "",
                                "SessionsCV": ""}
                        if str(self.type_folder) == 'Subject':
                            custom_vars = [("SubjectsGroup", ""), ("SubjectsTimepoint", ""), ("SubjectsDose", ""), ("SubjectsMagneticField", "")]
                        elif str(self.type_folder) == 'Experiment':
                            custom_vars = [("SessionsGroup", ""), ("SessionsTimepoint", ""), ("SessionsDose", ""), ("SessionsB0", ""), ("SessionsMagneticField", "")]
                        custom_file = [os.path.join(self.selected_item_path.get(), 'MR', self.selected_item_path.get().split('/')[-1] + "_Custom_Variables.txt")]
                    label_list = []
                    entry_list = []
                    num_custom_variables = 0
                    for x, my_var in enumerate(custom_vars):
                        if my_var[1] != None and my_var[1] != 'None' and my_var[1] != '' :
                            num_custom_variables += 1
                            # Custom Variable Label
                            if str(self.type_folder) == 'Subject':
                                text_label = str(custom_vars[x][0]).replace('Subjects','')
                            elif str(self.type_folder) == 'Experiment':
                                text_label = str(custom_vars[x][0]).replace('Sessions','')
                            label_n = ttk.Label(self.custom_var_labelframe, text=text_label)
                            label_n.grid(row=x+1, column=0, padx=5, pady=5, sticky=tk.NW)
                            label_list.append(label_n)
                            # Custom Variable Entry
                            entry_n = ttk.Entry(self.custom_var_labelframe, show='', state='disabled')
                            entry_n.var = tk.StringVar()
                            text_entry = str(custom_vars[x][1])
                            text_entry = '' if text_entry == 'None' else text_entry
                            entry_n.var.set(text_entry)
                            entry_n["textvariable"] = entry_n.var
                            entry_n.grid(row=x+1, column=1, padx=5, pady=5, sticky=tk.NW)
                            entry_list.append(entry_n)

                        # Button to modify the entry of the custom variable
                        def edit_handler(*args):
                            self.label_list1 = []
                            self.entry_list1 = []
                            all_custom_variables = len(custom_vars)
                            for x in range(1, all_custom_variables+1):
                                # Custom Variable Label
                                if str(self.type_folder) == 'Subject':
                                    text_label = str(custom_vars[x-1][0]).replace('Subjects','')
                                elif str(self.type_folder) == 'Experiment':
                                    text_label = str(custom_vars[x-1][0]).replace('Sessions','')
                                label_n1 = ttk.Label(self.custom_var_labelframe, text=text_label)
                                label_n1.grid(row=x, column=0, padx=5, pady=5, sticky=tk.NW)
                                self.label_list1.append(label_n1)
                                # Custom Variable Entry
                                entry_n1 = ttk.Entry(self.custom_var_labelframe, show='', state='disabled')
                                entry_n1.var = tk.StringVar()
                                text_entry1 = str(custom_vars[x-1][1])
                                text_entry1 = '' if text_entry1 == 'None' else text_entry1
                                entry_n1.var.set(text_entry1)
                                entry_n1["textvariable"] = entry_n1.var
                                entry_n1.grid(row=x, column=1, padx=5, pady=5, sticky=tk.NW)
                                self.entry_list1.append(entry_n1)
                            enable_buttons(self.entry_list1)
                            enable_buttons([confirm_button, reject_button])
                             
                        edit_button = ttk.Button(self.custom_var_labelframe, image=master.logo_edit, command=edit_handler,
                                                   style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        edit_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NW)

                        # Button to confirm changes
                        def accept_changes(*args):
                           # Save change on .txt file
                           try:
                               data = {}
                               data.update(info)
                               for e in range(len(self.entry_list1)):
                                   if str(self.type_folder) == 'Subject':
                                       new_key_sub = 'Subjects' + str(self.label_list1[e]["text"])
                                       data[new_key_sub] = self.entry_list1[e].var.get()
                                       if self.entry_list1[e].var.get() != "":
                                            new_key_ses = 'Sessions' + str(self.label_list1[e]["text"])
                                            data[new_key_ses] = self.entry_list1[e].var.get()
                                   if str(self.type_folder) == 'Experiment':
                                       new_key = 'Sessions' + str(self.label_list1[e]["text"])
                                       data[new_key] = self.entry_list1[e].var.get()
                               for custom_path_file in custom_file:        
                                write_table(custom_path_file, data)
                               display_custom_var()
                           except Exception as e: 
                              messagebox.showerror("XNAT-PIC Uploader", e)

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

            #self.n_custom_var.trace('w', display_custom_var)
            self.selected_item_path.trace('w', display_custom_var)
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

            # working_label = ttk.Label(self.frame_uploader, text='PC', image = master.computer_icon, compound=tk.LEFT, font = 'bold', anchor='center')
            # working_label.place(relx = 0.05, rely = 0.21, relwidth = 0.10, anchor = CENTER)
            # working_label1 = ttk.Label(self.frame_uploader, text="XNAT", image = master.server_icon, compound=tk.LEFT, font = 'bold', anchor='center')
            # working_label1.place(relx = 0.05, rely = 0.65, relwidth = 0.10, anchor = CENTER)

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
                            #params['custom_var_flag'] = self.n_custom_var.get()
                            # Check for existing custom variables file
                            
                            try:
                                # If the custom variables file is available
                                text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                                subject_data1 = read_table(text_file[0])
                                subject_data = {k: v or '' for (k, v) in subject_data1.items()}
                                # Define the subject_id and the experiment_id
                                # Controllo su stringa vuota
                                # self.sub.set(subject_data['Subject'])
                                # if self.sub.get() != subject_data['Subject']:
                                #     ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                #                             "The subject you are trying to retrieve does not match with the custom variables."
                                #                             "\n Would you like to continue?")
                                #     if ans != True:
                                #         return
                                # params['subject_id'] = self.sub.get()
                                # self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                #                         subject_data['SessionsGroup'], subject_data['SessionsTimepoint']]).replace(' ', '_'))
                                # params['experiment_id'] = self.exp.get()
                                # for var in subject_data.keys():
                                #     if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date']:
                                #         params[var] = subject_data[var]
                                                                
                                # Define the subject_id and the experiment_id if the custom variables file is not available
                                self.sub.set(exp.split('/')[-3].replace('.','_'))
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([exp.split('/')[-4].replace('_dcm', ''), exp.split('/')[-3].replace('.', '_'),
                                                             exp.split('/')[-2].replace('.', '_')]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()
                                for var in subject_data.keys():
                                    if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date']:
                                        params[var] = subject_data[var]
                                
                            except Exception as e:
                                print(e)
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
                    #params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(exp.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm',''), exp.split('/')[-2].replace('.','_')]).replace(' ', '_'))
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
                    #params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(experiment_to_upload, f) for f in os.listdir(experiment_to_upload) if f.endswith('.txt') 
                                                                                                                        and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id if the custom variables file is not available
                        if self.sub.get() == '--':
                            self.sub.set(experiment_to_upload.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([experiment_to_upload.split('/')[-3].replace('_dcm', ''), 
                                                    experiment_to_upload.split('/')[-2].replace('.','_')]).replace(' ', '_'))
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


if __name__ == "__main__":
    
    freeze_support()
    
    root = tk.Tk()
    check_credentials(root)
    app = xnat_pic_gui(root)
    root.mainloop()

           