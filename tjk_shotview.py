# coding=utf-8

__author__      = 'Alf Köhn-Seemann'
__email__       = 'koehn@igvp.uni-stuttgart.de'
__copyright__   = 'University of Stuttgart'
__license__     = 'MIT'

"""
bla
"""


import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import tkinter as tk

# to embed matplotlib into tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


fig1    = Figure()
ax1     = fig1.add_subplot()


# create a window and add charts
# widgets exist in a hierachy, "root" is highest level
root = tk.Tk()
root.title("TJ-K show-view")

path2data           = "/"
col_sideframe       = "#4C2A85"
col_sideframe_font  = "#FFF"

# create a frame which will be used to enter shot number and the path
# and also to display some information from the shot
side_frame = tk.Frame(root, bg=col_sideframe)
# Tkinter's layout/geometry manager "pack" will be used to position widgets
# note that "pack" is limited in precision compared to "place()" or "grid"
# but it is simple to use, position of widgets is declared in relation to 
# each other
side_frame.pack(side="left",    # possible options: left, right, top, bottom
                fill="y",       # widget fills entire space assigned to it,
                                # value controls how to fill space,
                                # both: expand horizontally + vertically
                                # x   : expand only horizontally
                                # y   : expand only vertically
               )

label = tk.Label(side_frame, 
                 text="shot-view", bg=col_sideframe, fg="#FFF", font=25)
label.pack(pady=50, padx=20)
#label.grid(row=0)

# quit buttom
button_quit = tk.Button(side_frame,
                        text="Quit",
                        command=root.destroy)
button_quit.pack(side=tk.BOTTOM, pady=10)


# side_frame will have an additional inner frame, which is organized via the
# geometry manager grid, and an outer which is mostly just for the quit button
# at the bottom
side_frame_inner = tk.Frame(side_frame, bg=col_sideframe)
side_frame_inner.pack(side="top", fill="y")

# user entry for shot number
shot_label  = tk.Label(side_frame_inner, 
                       text="shot",
                       bg=col_sideframe, fg="#FFF")
shot_label.grid(column=0, row=0, 
                sticky="E",
                padx=5, pady=5)
shot_entry  = tk.Entry(side_frame_inner)
shot_entry.grid(column=1, row=0,
                sticky="W",
                padx=5, pady=5)

# optional user entry where shot-data is located, i.e. path to data*
datapath_label  = tk.Label(side_frame_inner,
                           text="data path",
                       bg=col_sideframe, fg="#FFF")
datapath_label.grid(column=0, row=1, 
                    sticky="E",
                    padx=5, pady=5)
datapath_entry  = tk.Entry(side_frame_inner)
# write default value into field
datapath_entry.insert(0, path2data)
datapath_entry.grid(column=1, row=1,
                    sticky="W",
                    padx=5, pady=5)

timetraces_frame = tk.Frame(root)
timetraces_frame.pack(fill="both",
                      expand=True,  # assign additional space to widget box
                                    # if parent is larger than required for all
                                    # packed widgets, space will be distributed
                                    # among all widgets having set expand NE 0
                     )

# Canvas is used to generally draw pictures, graphs or any complex layout
canvas1 = FigureCanvasTkAgg(fig1, timetraces_frame)
canvas1.draw()
# return tk-widget associated with this canvas, then call pack to place it
canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

#tk.Button(frame, text="plot graph", command=plot).pack(pady=10)

# infinite loop waiting for events to occur and process them
root.mainloop()

