import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title('Tkinter Pack Layout')
root.geometry('300x200')


name_label = ttk.Label(root, text="Name:")
name_label.pack(side=tk.LEFT)

name_entry = ttk.Entry(root)
name_entry.pack(side=tk.LEFT)


button = ttk.Button(root, text="Submit")
button.pack(side=tk.LEFT)

root.mainloop()