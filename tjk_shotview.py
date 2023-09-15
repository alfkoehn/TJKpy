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
import numpy as np
import tkinter as tk
import os.path

# to embed matplotlib into tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import some TJ-K related function
import importlib    # required due to the dash in the filena,e
tjk = importlib.import_module("TJK-monitor")

# change some default properties of matplotlib
#plt.rcParams.update({'font.size':14})
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top']       = True
plt.rcParams['ytick.right']     = True


def validate_shotnumber(shot, status_label, datapath_entry):
    #{{{
    # note: functions for widget-level validation must return True or False

    col_ok      = "#00CC00"
    col_notok   = "#FF6666"

    shot    = shot_entry.get()
    if shot:
        if shot.isdigit() and int(shot) > 0:
            status_label.config(
                    text="status: shot #{0}".format(shot),
                    background=col_ok
                    )
            # update the field showing/setting the path to the data file
            path2data = get_tjkmonitor_datapath(shot_entry.get())
            datapath_entry.delete(0,tk.END)
            datapath_entry.insert(0, path2data)

            return True
        else:
            status_label.config(
                    text="status: shot must be an integer",
                    background=col_notok
                    )
            return False
    else:
        status_label.config(
                text="status: shot not entered",
                background=col_notok
                )
        return False
    #}}}


def get_tjkmonitor_datapath(shot):
    #{{{
    errValue    = -1

    fname_data  = 'shot{0}.dat'.format(shot)

    print( fname_data )

    # first, test if the folder from which this code is called has the data
    if os.path.isfile( fname_data ):
        return "."
    else:
        return errValue

    #}}}


def plot_timetraces(shot, 
                    status_label, datapath_entry,
                    fig, canvas
                   ):
    #{{{
    """
    TODO:
    [ ] only read and plot certain timetraces based on user choice
        [ ] show all available channel to user
        [ ] allow user to tick channels they want to plot
        [ ] store choices in dict (?)
        [ ] allow user to tick certain channels based on their role not 
            their exact name, e.g. P_abs2.455Ghz or n_e
    """

    col_ok      = "#00CC00"

    if not validate_shotnumber(shot, status_label, datapath_entry):
        return

    shot        = int(shot)
    fname_data  = "{0}/shot{1}.dat".format(datapath_entry.get(),shot)

    # get time axis and scale it to seconds
    time    = tjk.get_trace(shot, fname_in=fname_data, chName='Zeit [ms]')
    time   *= 1e-3

    #timetrace   = tjk.get_trace( shot, fname_in=fname_data, chName='I_Bh' )


    # idea: use dictionary for each diagnostics data stored via tjk-monitor
    #       which contains channel name in tjk-monitor, conversion factor
    #       (if a single conversion factor can be applied), 
    #       title for plot (including info about physical unit), comment,
    #       shotnumber when it was first introduced (maybe in comment)
    chCfg   = {}
    chCfg['B0']         = ['I_Bh', 0.24, 'mT', 
                           r'$B_0$ in $\mathrm{mT}$']
    chCfg['Pin2']       = ['2 GHz Richtk. forward', np.nan, '', 
                           r'$P_\mathrm{in}$ in $\mathrm{kW}$']
    chCfg['Pout2']      = ['2 GHz Richtk. backward', np.nan, '', 
                           r'$P_\mathrm{in}$ in $\mathrm{kW}$']
    chCfg['BoloSum']    = ['Bolo_sum', np.nan, '', 
                           r'$P_\mathrm{rad}$ in $\mathrm{W}$']
    chCfg['neMueller']  = ['Interferometer (Mueller)', 1, '1e17 m^-3', 
                           r'$\bar{n}_e$ in $10^{17}\,\mathrm{m}^{-3}$']

    #timetrace_Pin2  = tjk.get_trace(shot, fname_in=fname_data, chName=chCfg['Pin2'][0])
    #timetrace_Pout2 = tjk.get_trace(shot, fname_in=fname_data, chName=chCfg['Pout2'][0])

    #Pabs2   = ( calc_2GHzPower(timetrace_Pin2,  output='watt', direction='fw')
    #           -calc_2GHzPower(timetrace_Pout2, output='watt', direction='bw') )


    # number of timetraces to plot
    # will probably be changed as an optional keyword later
    n_traces    = 4

    data2plot   = ['B0', 'Pin2', 'neMueller', 'BoloSum']

    n_rows  = n_traces
    n_cols  = 1

    # fig return value of plt.subplot has list of all axes objects
    #for i, ax in enumerate(fig.axes):
    for ii in range(n_traces):
        print('**', ii, '**')
        ax  = fig.add_subplot(n_rows, n_cols, ii+1)
        timetrace   = tjk.get_trace( shot, fname_in=fname_data, 
                                     chName=chCfg[data2plot[ii]][0] 
                                   )
        if np.isfinite(chCfg[data2plot[ii]][1]):
            timetrace *= chCfg[data2plot[ii]][1]
        ax.plot( time, timetrace )
        ax.set_ylabel( chCfg[data2plot[ii]][3] )
    # add x-label only to bottom axes object
    ax.set_xlabel( 'time in s' )



    canvas1.draw()
    #}}}


fig1    = Figure()
#ax1     = fig1.add_subplot()


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

# write name of program at top
label = tk.Label(side_frame, 
                 text="shot-view", bg=col_sideframe, fg=col_sideframe_font, 
                 font=25)
label.pack(pady=50, padx=20)

# quit button at very bottom
button_quit = tk.Button(side_frame,
                        text="Quit",
                        command=root.destroy)
button_quit.pack(side=tk.BOTTOM, padx=5, pady=10, fill="x")


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
shot_entry  = tk.Entry(side_frame_inner, 
                       validatecommand=lambda: validate_shotnumber(
                           shot_entry.get(),
                           status_label,
                           datapath_entry),
                       #validate="key"  # not working for some reason
                       validate="focusout"
                      )
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
# write value into field based on shot-number
#path2data = get_tjkmonitor_datapath(shot_entry.get())
datapath_entry.insert(0, path2data)
datapath_entry.grid(column=1, row=1,
                    sticky="W",
                    padx=5, pady=5)

# plot button (for time traces)
plot_button = tk.Button(side_frame_inner,
                        text="Plot time traces",
                        command=lambda: plot_timetraces(shot_entry.get(), 
                                                        status_label,
                                                        datapath_entry,
                                                        fig1, canvas1
                                                       )
                       )
plot_button.grid(row=2, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=10)

# some information deduced from time traces




timetraces_frame = tk.Frame(root)
timetraces_frame.pack(fill="both",
                      expand=True,  # assign additional space to widget box
                                    # if parent is larger than required for all
                                    # packed widgets, space will be distributed
                                    # among all widgets having set expand NE 0
                     )

# status massage field at top
status_label    = tk.Label(timetraces_frame,
                           text="status: ready to go", 
                           #bg=col_sideframe, fg=col_sideframe_font
                          )
status_label.pack(anchor="nw")

# Canvas is used to generally draw pictures, graphs or any complex layout
canvas1 = FigureCanvasTkAgg(fig1, timetraces_frame)
canvas1.draw()
# return tk-widget associated with this canvas, then call pack to place it
canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

#tk.Button(frame, text="plot graph", command=plot).pack(pady=10)

# infinite loop waiting for events to occur and process them
root.mainloop()

