import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Treeview con Scrollbar")
        
        # Configuro la griglia del root per far crescere la colonna 0 e la riga 0
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_treeview()
    
    def setup_treeview(self):
        columns = ("Id", "Subject", "Experiment", "Modality")
        
        # Treeview
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar verticale
        self.tree_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Collego scrollbar e treeview
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
        # Inserisco dati di esempio
        for i in range(20):
            self.tree.insert("", "end", values=(i, f"Subject {i}", f"Experiment {i}", "MRI"))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
