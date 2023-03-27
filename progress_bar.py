# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 2022

@author: Riccardo Gambino
"""

"""
Progress bar class.
"""
import tkinter as tk
#import tkinter.ttk as ttk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import HORIZONTAL
# from threading import Thread
# import time

class ProgressBar():
    def __init__(self, root, bar_title):

        self.title = bar_title
        self.popup = tk.Toplevel(root)
        self.popup.grab_set() # when you show the popup
        self.popup.geometry("%dx%d+%d+%d" % (500, 100, 700, 500))
        self.popup.resizable(False, False)
        self.popup.title(bar_title)
        self.progress_var = tk.DoubleVar()
        self.bar_length = 400
        self.bar_maximum = 100
        self.label = ttk.Label(self.popup, text='Loading ...', anchor=tk.CENTER, style="SubTitle.TLabel")
        self.label.pack(side='top', fill='x', anchor=tk.CENTER, padx=10)
        self.caption = ttk.Label(self.popup, text='', font=("Calibri", 10), anchor=tk.CENTER)
        self.caption.pack(side='bottom', fill='x', anchor=tk.CENTER, padx=10)

    def show_step(self, index, total):
        self.step.config(text=str(index) + ' / ' + str(total))
        self.popup.update()

    def set_caption(self, text):
        self.caption.config(text='')
        self.caption.config(text=text)
        self.popup.update()
        
    def start_determinate_bar(self):

        print('Starting progress bar...')
        self.progressbar = ttk.Progressbar(self.popup, variable=self.progress_var,
                                             orient=HORIZONTAL, 
                                            length=self.bar_length, mode='determinate', maximum=self.bar_maximum)
        self.progressbar.pack(side='left', expand=True, anchor=tk.CENTER, padx=10)
        self.step = ttk.Label(self.popup, text="", font=("Calibri", 10), anchor=tk.CENTER)
        self.step.pack(side='left', anchor=tk.CENTER, padx=10, expand=True)

    def start_indeterminate_bar(self):

        print('Starting progress bar...')
        self.progressbar = ttk.Progressbar(self.popup, 
                                            orient=HORIZONTAL, 
                                            length=self.bar_length, mode='indeterminate')
        self.progressbar.pack(side='left', expand=True, anchor=tk.CENTER, padx=10)
        self.step = ttk.Label(self.popup, text="", font=("Calibri", 10), anchor=tk.CENTER)
        self.step.pack(side='left', anchor=tk.CENTER, padx=10, expand=True)
        self.progressbar.start()

    def update_bar(self, step=0.001):
        self.progressbar.step(step)
        self.progressbar.update()
             
    def update_progressbar(self, current_step, max_step):
        progress = int(current_step * self.bar_maximum / max_step)
        self.progress_var.set(progress)
        self.popup.update()
    
    def stop_progress_bar(self):
        print("Stopping progress bar...")
        self.progressbar.stop()
        self.popup.destroy()
        
