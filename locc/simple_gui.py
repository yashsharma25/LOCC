import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Simple GUI")
root.geometry("500x500")

# create a label
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=10)

# create an entry widget
entry = tk.Entry(root, width=20)
entry.pack(pady=10)

def on_button_click():
    user_text = entry.get()
    messagebox.showinfo("Information", f"You entered: {user_text}")

# create a button
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(side='bottom', pady=10)

# start main event loop
root.mainloop()
