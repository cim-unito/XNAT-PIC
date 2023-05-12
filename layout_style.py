# -*- coding: utf-8 -*-
"""
Created on May 30, 2022

@author: Riccardo Gambino, Francesco Gammaraccio

"""
from pyparsing import White
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap.themes.standard 
import tkinter as tk
from PIL import Image, ImageTk
import json

PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
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
MAIN_TITLE_FONT = ("Helvetica", 36)
TITLE_FONT = ("Inkfree", 36, "italic")
UNDERTITLE_FONT = ("Inkfree", 24, "italic")
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
SMALL_FONT_3 = ("Calibri", 12)
SMALL_FONT_4 = ("Calibri", 14, "bold")
KEYWORD_FONT = ("Calibri", 8)
ATTACHED_FONT = ("Calibri", 8, "underline")
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3

with open("layout_colors.json", "r") as theme_file:
    theme_colors = json.load(theme_file)

class MyStyle():

    def __init__(self, style_name):

        self.style_name = style_name
        self.style = ttk.Style(theme=self.style_name)

    def configure(self):
        
        # Configure Buttons
        self.style.configure('TButton', font=SMALL_FONT, cursor=CURSOR_HAND)
        self.style.configure("Secondary.TButton", font=SMALL_FONT_3)
        self.style.configure("Secondary1.TButton", font=SMALL_FONT_4)
        self.style.configure("WithoutBack.TButton", padding=2, background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["light"], borderwidth=0)
        self.style.map("WithoutBack.TButton", background=[('active', theme_colors[self.style_name]["colors"]["bg"]), ('disabled', theme_colors[self.style_name]["colors"]["bg"])])
        self.style.configure("Popup.TButton", padding=2, background=theme_colors[self.style_name]["colors"]["bg"], foreground="black", borderwidth=0, font=SMALL_FONT)
        self.style.map("Popup.TButton", background=[('active', theme_colors[self.style_name]["colors"]["bg"]), ('disabled', theme_colors[self.style_name]["colors"]["bg"])])
        self.style.configure("MainPopup.TButton", padding=2, font=SMALL_FONT, width=15)
        self.style.configure("Keyword.TButton", font=KEYWORD_FONT, background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["primary"], borderwidth=1)
        self.style.map("Keyword.TButton", background=[("active", theme_colors[self.style_name]["colors"]["bg"])], foreground=[("active", theme_colors[self.style_name]["colors"]["primary"])])

        # Configure Labels
        self.style.configure("MainTitle.TLabel", font=MAIN_TITLE_FONT, foreground=theme_colors[self.style_name]["colors"]["primary"])
        self.style.configure("Title.TLabel", background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["info"], font=TITLE_FONT)
        self.style.configure("Popup.TLabel", background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["primary"], font=ATTACHED_FONT)
        self.style.configure("UnderTitle.TLabel", background=theme_colors[self.style_name]["colors"]["bg"], foreground="black", font=UNDERTITLE_FONT)
        self.style.configure("Error.TLabel", font=KEYWORD_FONT, foreground=theme_colors[self.style_name]["colors"]["danger"])
        self.style.configure("SubTitle.TLabel", font=SMALL_FONT, foreground=theme_colors[self.style_name]["colors"]["primary"])
        
        # Configure OptionMenus
        self.style.configure("TMenubutton", background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["primary"],
                                            arrowcolor=theme_colors[self.style_name]["colors"]["primary"])
        self.style.map("TMenubutton", background=[('active', theme_colors[self.style_name]["colors"]["bg"])])

        # Configure Entries
        self.style.configure("TEntry", disabledbackground=LIGHT_GREY)
        self.style.map("TEntry", background=[('active', theme_colors[self.style_name]["colors"]["bg"]), ('disabled', LIGHT_GREY)], disabledbackground=[('active', LIGHT_GREY), ('disabled', LIGHT_GREY)],
                                        highlightthickness=[("active", 10)])

        # Configure Labelframes
        self.style.configure("Hidden.TLabelframe", background=theme_colors[self.style_name]["colors"]["bg"], foreground=theme_colors[self.style_name]["colors"]["bg"], borderwidth=0, padding=0)

        self.style.configure('TSeparator', padding=(0, 15, 0, 15), borderwidth=4)

    def get_style(self):
        return self.style
