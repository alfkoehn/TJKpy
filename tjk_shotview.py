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
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

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

    # first, test if the folder from which this code is called has the data
    if os.path.isfile( fname_data ):
        return "."
    else:
        shot_path   = tjk.get_shot_path(shot)
        if isinstance(shot_path, str):
            shot_path += 'interferometer/'
            return shot_path
        else:
            return errValue

    #}}}


def plot_timetraces(shot, 
                    status_label, datapath_entry,
                    fig, canvas,
                    timetraces_options
                   ):
    #{{{
    """
    TODO:
    [ ] only read and plot certain timetraces based on user choice
        [ ] show all available channel to user (really all...?)
        [ ] allow user to tick channels they want to plot
        [ ] store choices in dict (?)
        [ ] allow user to tick certain channels based on their role not 
            their exact name, e.g. P_abs2.455Ghz or n_e
    """
   
    # plot needs to be cleared otherwise x- and y-axis will be "over-drawn"
    fig.clf()

    col_ok      = "#00CC00"

    if not validate_shotnumber(shot, status_label, datapath_entry):
        return

    shot        = int(shot)
    fname_data  = "{0}/shot{1}.dat".format(datapath_entry.get(),shot)

    # get time axis and scale it to seconds
    time    = tjk.get_trace(shot, fname_in=fname_data, chName='Zeit [ms]')
    time   *= 1e-3

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
    chCfg['Pabs2']      = ['Pabs2', np.nan, '', 
                           r'$P_\mathrm{abs}$ in $\mathrm{kW}$']
    chCfg['BoloSum']    = ['Bolo_sum', np.nan, '', 
                           r'$P_\mathrm{rad}$ in $\mathrm{W}$']
    chCfg['neMueller']  = ['Interferometer (Mueller)', 1, '1e17 m^-3', 
                           r'$\bar{n}_e$ in $10^{17}\,\mathrm{m}^{-3}$']

    # get timetraces of diodes installed at directional coupler in 2.45 GHz 
    # transmission line and calculate P_abs = P_in - P_out
    timetrace_Pin2  = tjk.get_trace(shot, fname_in=fname_data, chName=chCfg['Pin2'][0])
    timetrace_Pout2 = tjk.get_trace(shot, fname_in=fname_data, chName=chCfg['Pout2'][0])
    timetrace_Pabs2  = ( tjk.calc_2GHzPower(timetrace_Pin2,  output='watt', direction='fw')
                        -tjk.calc_2GHzPower(timetrace_Pout2, output='watt', direction='bw') )

    # get timetrace of interferometer signal, optionally
    #   correct for drift
    #   correct for offset
    #   calculate actual electron plasma density
    timetrace_ne    = tjk.get_trace(shot, fname_in=fname_data, chName=chCfg['neMueller'][0])
    # number of points for offset calculation and drift correction
    n_pts_offset    = 100
    # optionally, correct for drift by subtracting straight line (slope)
    # between offset before plasma turn-on and offset after plasma turn-off
    if timetraces_options['interf_drift_correct']:
        offset_start    = np.mean(timetrace_ne[:n_pts_offset])
        offset_end      = np.mean(timetrace_ne[(-1*n_pts_offset):])
        print("offset_start = {0}, offset_end = {1}".format(offset_start, offset_end))
        # TODO: y = m*x + b, m = (y2-y1)/(x2-x1)
        #       ==> y2 and y1 are just the offset values, neglecting the drift in the offset itself
        #       ==> x2 and x1 and harder to get, we actually need to determine the jump-positions,
        #           i.e. when the plasma is turned on and turned off again
        #       then the function can be subtracted from original function of correct for drift
        #       ==> new = old - ((offset_1-offset_0)/(jump_off-jump_on)*time + offset_0)
        #       idea: do as with previous IDL version (look for min and max in derivative of interferometer)
        #       as an easy check, include a button for marking the jumps in plot
    if timetraces_options['interf_calc_ne']:
        # TODO: for 'Interferometer (Mueller)' and 'Interferometer Phase' the
        #       scaling factor is 3.883e17 until the damage and repair by e.ho
        #       in summer 2022, then it was changed to half of that.
        #       for 'Density (old)' and befor the factor is 6.7e16
        timetrace_ne    *= 3.883#e17


    # number of timetraces to plot
    # will probably be changed as an optional keyword later
    n_traces    = 4

    data2plot   = ['B0', 'Pabs2', 'neMueller', 'BoloSum']

    n_rows  = n_traces
    n_cols  = 1

    # fig return value of plt.subplot has list of all axes objects
    #for i, ax in enumerate(fig.axes):
    for ii in range(n_traces):
        print('**', ii, data2plot[ii], '**')
        ax  = fig.add_subplot(n_rows, n_cols, ii+1)
        if data2plot[ii] == 'Pabs2':
            timetrace   = timetrace_Pabs2
            ylabel      = r'$P_\mathrm{abs}$ in $\mathrm{kW}$'
        elif data2plot[ii] == 'neMueller':
            timetrace   = timetrace_ne
            if timetraces_options['interf_calc_ne']:
                ylabel      = r'$\bar{n}_e$ in $10^{17}\,\mathrm{m}^{-3}$'
            else:
                ylabel      = r'$\bar{n}_e$ in a.u.'
        else:
            timetrace   = tjk.get_trace( shot, fname_in=fname_data, 
                                         chName=chCfg[data2plot[ii]][0] 
                                       )
            ylabel      = chCfg[data2plot[ii]][3]
        if np.isfinite(chCfg[data2plot[ii]][1]):
            timetrace *= chCfg[data2plot[ii]][1]
        ax.plot( time, timetrace )
        ax.set_ylabel( ylabel )
    # add x-label only to bottom axes object
    ax.set_xlabel( 'time in s' )

    canvas.draw()
    #}}}


def checkbutton_clicked(var, str_var, timetraces_options, status_label):
    #{{{

    col_ok      = "#00CC00"

    if var.get():
        status_label.config(
                text="status: {0} activated".format(str_var),
                background=col_ok
                )
        timetraces_options[str_var] = 1
    else:
        status_label.config(
                text="status: {0} deactivated".format(str_var),
                background=col_ok
                )
        timetraces_options[str_var] = 0
    #}}}


fig1    = Figure()

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
                       bg=col_sideframe, fg=col_sideframe_font)
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

# dictionary for some optional data processing stuff
timetraces_options  = {
        'B0'                    : 1,
        'interf_drift_correct'  : 0,
        'interf_offset_correct' : 0,
        'interf_calc_ne'        : 0,
        'P8GHz_in'              : 0,
        'BoloSum'               : 0,
        }
# plot button (for time traces)
plot_button = tk.Button(side_frame_inner,
                        text="Plot time traces",
                        command=lambda: plot_timetraces(shot_entry.get(), 
                                                        status_label,
                                                        datapath_entry,
                                                        fig1, canvas1,
                                                        timetraces_options
                                                       )
                       )
plot_button.grid(row=2, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=10)


# some checkboxes to activate/deactivate certain timetraces and certain
# data processing stuff
# checkbutton for plotting timetrace of B0
plot_B0_var                 = tk.IntVar(value=timetraces_options['B0'])
plot_B0_checkbutton         = tk.Checkbutton(side_frame_inner, 
                                             text="include B0",
                                             variable=plot_B0_var,
                                             onvalue=1, offvalue=0,
                                             state=tk.NORMAL,
                                             #bd=0,
                                             #bg=col_sideframe, 
                                             #fg=col_sideframe_font,    # this makes problems, tick seems to become invisible (?)
                                             command=lambda: checkbutton_clicked(
                                                 plot_B0_var,
                                                 "B0",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
plot_B0_checkbutton.grid(row=3, column=1, sticky=tk.W, padx=5)
# checkbutton for drift correction
interf_drift_var            = tk.IntVar()
interf_drift_checkbutton    = tk.Checkbutton(side_frame_inner, 
                                             text="correct interf. drift",
                                             variable=interf_drift_var,
                                             onvalue=1, offvalue=0,
                                             state=tk.DISABLED,
                                             command=lambda: checkbutton_clicked(
                                                 interf_drift_var,
                                                 "interf_drift_correct",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
interf_drift_checkbutton.grid(row=4, column=1, sticky=tk.W, padx=5)
# checkbutton for calculating line-averaged density timetrace
interf_neCalc_var           = tk.IntVar()
interf_neCalc_checkbutton   = tk.Checkbutton(side_frame_inner, 
                                             text="calculate n_e",
                                             variable=interf_neCalc_var,
                                             onvalue=1, offvalue=0, 
                                             #bd=0,
                                             #bg=col_sideframe, 
                                             #fg=col_sideframe_font,    # this makes problems, tick seems to become invisible (?)
                                             command=lambda: checkbutton_clicked(
                                                 interf_neCalc_var,
                                                 "interf_calc_ne",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
interf_neCalc_checkbutton.grid(row=5, column=1, sticky=tk.W, padx=5)
# checkbutton for correction for offset at end
interf_offsetCorr_var   = tk.IntVar()
interf_offsetCorr_check = tk.Checkbutton(side_frame_inner,
                                         text="correct offset",
                                         variable=interf_offsetCorr_var,
                                         state=tk.DISABLED,
                                         command=lambda: checkbutton_clicked(
                                             interf_offsetCorr_var,
                                             "interf_offset_correct",
                                             timetraces_options,
                                             status_label)
                                         )
interf_offsetCorr_check.grid(row=6, column=1, sticky=tk.W, padx=5)
# checkbutton for ingoing 8 GHz measured via Kasparek diode
P8GHz_in_var    = tk.IntVar()
P8GHz_in_check  = tk.Checkbutton(side_frame_inner,
                                 text="include P_in8GHz",
                                 variable=P8GHz_in_var,
                                 state=tk.DISABLED,
                                 command=lambda: checkbutton_clicked(
                                    P8GHz_in_var,
                                    "P8GHz_in",
                                    timetraces_options,
                                    status_label)
                                 )
P8GHz_in_check.grid(row=7, column=1, sticky=tk.W, padx=5)

# checkbutton for including the Bolometer sum channel
boloSum_var     = tk.IntVar()
boloSum_check   = tk.Checkbutton(side_frame_inner,
                                 text="include Bolo_sum",
                                 variable=boloSum_var,
                                 state=tk.DISABLED,
                                 command=lambda: checkbutton_clicked(
                                     boloSum_var,
                                     "BoloSum",
                                     timetraces_options,
                                     status_label)
                                 )
boloSum_check.grid(row=8, column=1, sticky=tk.W, padx=5)



# some information deduced from time traces
# calculate line-averaged density as value obtained from plasma-off
# calculate non-gastype corrected (i.e. displayed) neutral gas pressure at offset_0



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

# matplotlib toolbar
plot_toolbar    = NavigationToolbar2Tk( 
        canvas1, 
        timetraces_frame, 
        #pack_toolbar=False,      # recommended, but does not work for newer version of some libraries
        )
plot_toolbar.config(background='white')
plot_toolbar._message_label.config(background='white')
# initialise toolbar object
plot_toolbar.update()
# pack toolbar into GUI
plot_toolbar.pack(anchor=tk.W, side=tk.BOTTOM, fill=tk.X)

# return tk-widget associated with this canvas, then call pack to place it
# note: needs to be called after initializing toolbar
canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

# infinite loop waiting for events to occur and process them
root.mainloop()

