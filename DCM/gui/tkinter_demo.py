from tkinter import *
from tkinter import ttk

from tkinter import *
from tkinter import ttk

#https://tkdocs.com/tutorial/firstexample.html this link explains this code
def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(round(0.3048 * value, 4))
    except ValueError:
        pass


root = Tk() #root creates a Tk object and allows you to createa window
root.title("Feet to Meters") #title for the window

mainframe = ttk.Frame(root, padding=(3, 3, 12, 12)) 
#frame(parent window)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
#grid places the frame directly inside the applicatoin window

feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()