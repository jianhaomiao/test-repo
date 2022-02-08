from tkinter import *
from tkinter import ttk

# Drop down options
options = [
	' ',
    'Little Queen Charlotte',
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

# Create Tkinter
root = Tk()
root.geometry('444x500')

frm = ttk.Frame(root, padding=10)
frm.grid()

paddings = {'padx': 5, 'pady': 5}

# Define creation functions
def fp_checkbox(root):
    v = IntVar()
    c = Checkbutton(root, variable=v, onvalue=1, offvalue=0)
    c.grid(column=0, row=0, **paddings)

def hero_dropdown(root, checkbox, option):
    h = StringVar()
    b = IntVar()

    h.set(options[0])
    c = Checkbutton(root, variable=b, onvalue=1, offvalue=0)
    c.grid(column=checkbox[0], row=checkbox[1])

    d = OptionMenu(root, h, *options)
    d.config(width=15)
    d.grid(column=option[0], row=option[1], sticky="ew", **paddings)

# Create GUI
fp_checkbox(root)

hero_dropdown(root, (0, 1), (1, 1))
hero_dropdown(root, (0, 2), (1, 2))
hero_dropdown(root, (0, 3), (1, 3))
hero_dropdown(root, (0, 4), (1, 4))
hero_dropdown(root, (0, 5), (1, 5))

hero_dropdown(root, (4, 1), (3, 1))
hero_dropdown(root, (4, 2), (3, 2))
hero_dropdown(root, (4, 3), (3, 3))
hero_dropdown(root, (4, 4), (3, 4))
hero_dropdown(root, (4, 5), (3, 5))

root.mainloop()
