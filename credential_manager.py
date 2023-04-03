# -*- coding: utf-8 -*-
"""
Created on May 30, 2022

@author: Riccardo Gambino

"""
import os
import getpass
import tkinter as tk
import ttkbootstrap as ttk
from access_manager import CURSOR_HAND
from accessory_functions import disable_buttons

PATH_IMAGE = "images\\"

class CredentialManager():

    def __init__(self, root):

        self.root = root

        self.root.title("XNAT-PIC ~ Credentials")
        self.root.geometry("+%d+%d" % (500, 250))
        self.root.iconbitmap(PATH_IMAGE + "logo3.ico")
        # self.popup = ttk.Toplevel(self.root)
        self.popup = ttk.Frame(self.root)
        self.popup.pack(fill='both', expand=1)
        
        self.popup.tk_label = ttk.Label(self.popup, text="XNAT-PIC Configuration")
        self.popup.tk_label.grid(row=0, column=1, padx=10, pady=10)

        # XNAT-PIC secretUser
        self.popup.label_secretUser = ttk.Label(self.popup, text="User")
        self.popup.label_secretUser.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.popup.entry_secretUser = ttk.Entry(self.popup, show="", width=50, state='disabled')
        self.popup.entry_secretUser.var = tk.StringVar()
        self.popup.entry_secretUser["textvariable"] = self.popup.entry_secretUser.var
        self.popup.entry_secretUser.grid(row=1, column=1, padx=5, pady=5)
        self.popup.entry_secretUser.var.set(getpass.getuser())

        # User CheckButton
        def enable_user_entry(*args):
            if self.popup.change_user_btn_var.get() == 1:
                self.popup.entry_secretUser.configure(state='normal')
            else:
                self.popup.entry_secretUser.configure(state='disabled')
        self.popup.change_user_btn_var = tk.IntVar()
        self.popup.change_user_btn= ttk.Checkbutton(self.popup, variable=self.popup.change_user_btn_var, onvalue=1, offvalue=0, text="Change User")
        self.popup.change_user_btn.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.popup.change_user_btn_var.trace('w', enable_user_entry)
        
        # XNAT-PIC secretKey
        def enable_secretPIN(*args):
            if self.popup.entry_secretKey_2.var.get() != '':
                self.popup.entry_secretPIN.configure(state='normal')
                self.popup.entry_secretPIN_2.configure(state='normal')
            else:
                self.popup.entry_secretPIN.configure(state='disabled')
                self.popup.entry_secretPIN_2.configure(state='disabled')
        self.popup.label_secretKey = ttk.Label(self.popup, text="Insert Key")
        self.popup.label_secretKey.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.popup.entry_secretKey = ttk.Entry(self.popup, show="*", width=50)
        self.popup.entry_secretKey.var = tk.StringVar()
        self.popup.entry_secretKey["textvariable"] = self.popup.entry_secretKey.var
        self.popup.entry_secretKey.grid(row=2, column=1, padx=5, pady=5)
        
        # Re-insert secretKey
        def check_Key(*args):
            try:
                self.popup.checked_key.destroy()
            except:
                pass
            if self.popup.entry_secretKey_2.var.get() != '':
                if self.popup.entry_secretKey.var.get() != self.popup.entry_secretKey_2.var.get():
                    self.popup.checked_key = ttk.Label(self.popup, text="Password does not correspond!", foreground='red')
                    self.popup.checked_key.grid(row=3, column=2, padx=5, sticky=tk.W)
                else:
                    self.popup.checked_key = ttk.Label(self.popup, text="OK!", foreground='green')
                    self.popup.checked_key.grid(row=3, column=2, padx=5, sticky=tk.W)

        self.popup.label_secretKey_2 = ttk.Label(self.popup, text="Insert Key again")
        self.popup.label_secretKey_2.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.popup.entry_secretKey_2 = ttk.Entry(self.popup, show="*", width=50)
        self.popup.entry_secretKey_2.var = tk.StringVar()
        self.popup.entry_secretKey_2["textvariable"] = self.popup.entry_secretKey_2.var
        self.popup.entry_secretKey_2.grid(row=3, column=1, padx=5, pady=5)
        self.popup.entry_secretKey_2.var.trace('w', check_Key)
        self.popup.entry_secretKey_2.var.trace('w', enable_secretPIN)

        # XNAT-PIC secretPIN
        def enable_next_btn(*args):
            if self.popup.entry_secretPIN_2.var.get() != '':
                self.popup.next_btn.configure(state='normal')
            else:
                self.popup.next_btn.configure(state='disabled')
        self.popup.label_secretPIN = ttk.Label(self.popup, text="Insert PIN")
        self.popup.label_secretPIN.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.popup.entry_secretPIN = ttk.Entry(self.popup, show="*", width=50, state='disabled')
        self.popup.entry_secretPIN.var = tk.StringVar()
        self.popup.entry_secretPIN["textvariable"] = self.popup.entry_secretPIN.var
        self.popup.entry_secretPIN.grid(row=4, column=1, padx=5, pady=5)

        # Re-insert secretPIN
        def check_PIN(*args):
            try:
                self.popup.checked_PIN.destroy()
            except:
                pass
            if self.popup.entry_secretPIN_2.var.get() != '':
                if self.popup.entry_secretPIN.var.get() != self.popup.entry_secretPIN_2.var.get():
                    self.popup.checked_PIN = ttk.Label(self.popup, text="Password does not correspond!", foreground='red')
                    self.popup.checked_PIN.grid(row=5, column=2, padx=5, sticky=tk.W)
                else:
                    self.popup.checked_PIN = ttk.Label(self.popup, text="OK!", foreground='green')
                    self.popup.checked_PIN.grid(row=5, column=2, padx=5, sticky=tk.W)

        self.popup.label_secretPIN_2 = ttk.Label(self.popup, text="Insert PIN again")
        self.popup.label_secretPIN_2.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        self.popup.entry_secretPIN_2 = ttk.Entry(self.popup, show="*", width=50, state='disabled')
        self.popup.entry_secretPIN_2.var = tk.StringVar()
        self.popup.entry_secretPIN_2["textvariable"] = self.popup.entry_secretPIN_2.var
        self.popup.entry_secretPIN_2.grid(row=5, column=1, padx=5)
        self.popup.entry_secretPIN_2.var.trace('w', check_PIN)
        self.popup.entry_secretPIN_2.var.trace('w', enable_next_btn)

        # NEXT Button
        def next():
            self.popup.destroy()
            self.write_credentials(self.popup.entry_secretUser.var, self.popup.entry_secretKey.var, self.popup.entry_secretPIN.var)
        self.popup.next_text = tk.StringVar() 
        self.popup.next_btn = ttk.Button(self.popup, textvariable=self.popup.next_text, command=next, cursor=CURSOR_HAND, takefocus=0, state='disabled')
        self.popup.next_text.set("Next")
        self.popup.next_btn.grid(row=6, column=1, padx=10, pady=10)

    
    def write_credentials(self, user, psw, pin):

        dir = os.getcwd().replace('\\', '/')
        head, tail = os.path.split(dir)

        with open(head + '/.env', 'w+') as credential_file:
            credential_file.write('secretUser=' + '"' + str(user.get()) + '"' + '\n')
            credential_file.write('secretKey=' + '"' + str(psw.get()) + '"' + '\n')
            credential_file.write('secretPIN=' + '"' + str(pin.get()) + '"' + '\n')
            credential_file.write('bufferSize1=64\n')
            credential_file.write('bufferSize2=1024')

       

    def change_credentials(self, user, psw, pin):

        dir = os.getcwd().replace('\\', '/')
        head, tail = os.path.split(dir)
        with open(head + '/.env', 'r') as credential_file:
            data = credential_file.read().split('\n')
            for i, d in enumerate(data):
                if 'secretUser' in d:
                    data.remove(d)
                    data.insert(i, 'secretUser=' + '"' + str(user) + '"')
                elif 'secretKey' in d:
                    data.remove(d)
                    data.insert(i, 'secretKey=' + '"' + str(psw) + '"')
                elif 'secretPIN' in d:
                    data.remove(d)
                    data.insert(i, 'secretPIN=' + '"' + str(pin) + '"')

        with open(head + '/.env', 'w+') as credential_file:
            for d in data:
                credential_file.write(d + '\n')
