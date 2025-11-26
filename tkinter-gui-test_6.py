import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title('Login')
root.geometry("320x200")


fields = {}

fields['username_label'] = ttk.Label(root, text='Username:')
fields['username'] = ttk.Entry(root)

fields['password_label'] = ttk.Label(root, text='Password:')
fields['password'] = ttk.Entry(root, show="*")


for field in fields.values():
    field.pack(anchor=tk.W, padx=10, pady=5, fill=tk.X)

ttk.Button(text='Login').pack(anchor=tk.W, padx=10, pady=10)

root.mainloop()