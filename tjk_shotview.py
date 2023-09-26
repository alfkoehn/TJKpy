# coding=utf-8

__author__      = 'Alf Köhn-Seemann'
__email__       = 'koehn@igvp.uni-stuttgart.de'
__copyright__   = 'University of Stuttgart'
__license__     = 'MIT'

"""
bla
"""


from pathlib import Path
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
            shot_path = Path(shot_path + "interferometer/")
            #shot_path += 'interferometer/'
            return shot_path
        elif Path.exists(shot_path):
            shot_path = shot_path / "interferometer/"
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
    #fname_data  = "{0}/shot{1}.dat".format(datapath_entry.get(),shot)
    fname_data  = Path(datapath_entry.get() + '/shot'  + str(shot) + '.dat')

    # get time axis and scale it to seconds
    time    = tjk.get_trace(shot, fname_in=fname_data, chName='Zeit [ms]')
    time   *= 1e-3

    # get number of timetraces to be plotted based on choice made by user
    # loop through dictionary and sum up every key starting with "plot"
    n_traces    = 0
    for key in timetraces_options:
        if key.startswith('plot'):
            n_traces    += timetraces_options[key]

    # idea: use dictionary for each diagnostics data stored via tjk-monitor
    #       which contains 
    #         (1) channel name in tjk-monitor
    #         (2) conversion factor (if single factor makes sense)
    #         (3) physical units after applying conversion factor
    #         (4) y-axis label for plot
    #         (5) optional comment
    # note that the key-name MUST be identical to timetraces_options
    #   --> this should probably be changed somehow in a future version
    #       as it is errorprone this way
    chCfg   = {}
    chCfg['plot_B0']        = ['I_Bh', 0.24, 'mT', 
                               r'$B_0$ in $\mathrm{mT}$']
    chCfg['plot_Tcoil']     = ['Coil Temperature', 1, 'C', 
                               r'$T_\mathrm{coil}$ in $^\circ\mathrm{C}$']
    chCfg['plot_P2GHz_in']  = ['2 GHz Richtk. forward', np.nan, '', 
                               r'$P_\mathrm{in}$ in $\mathrm{kW}$']
    chCfg['plot_P2GHz_out'] = ['2 GHz Richtk. backward', np.nan, '', 
                               r'$P_\mathrm{in}$ in $\mathrm{kW}$']
    chCfg['plot_P2GHz_abs'] = ['Pabs2', np.nan, '', 
                               r'$P_\mathrm{abs}$ in $\mathrm{kW}$']
    chCfg['plot_P8GHz_in']  = ['8 GHz power', np.nan, '', 
                               r'$P_\mathrm{in}$ in $\mathrm{kW}$']
    chCfg['plot_BoloSum']   = ['Bolo_sum', np.nan, '', 
                               r'$P_\mathrm{rad}$ in $\mathrm{W}$']
    if shot >= 13316:   # TODO: this number needs to be corrected to some lower shotnumber
        chCfg['plot_interf']    = ['Interferometer digital', 1, '1e17 m^-3', 
                                   r'$\bar{n}_e$ in a.u.']
    else:
        chCfg['plot_interf']    = ['Interferometer (Mueller)', 1, '1e17 m^-3', 
                                   r'$\bar{n}_e$ in a.u.']

    n_rows      = n_traces
    n_cols      = 1
    plot_count  = 1
    for key in timetraces_options:
        if key.startswith('plot') and (timetraces_options[key] == 1):
            print( key, timetraces_options[key] )
            ax  = fig.add_subplot(n_rows, n_cols, plot_count)

            # P_abs for 2.45 GHz is calculated using two timetraces
            if key == 'plot_2GHz_abs':
                timetrace_Pin2  = tjk.get_trace(shot, fname_in=fname_data, 
                                                chName=chCfg['plot_P2GHz_in'][0])
                timetrace_Pout2 = tjk.get_trace(shot, fname_in=fname_data, 
                                                chName=chCfg['plot_P2GHz_out'][0])
                timetrace       = ( tjk.calc_2GHzPower(timetrace_Pin2,  output='watt', direction='fw')
                                   -tjk.calc_2GHzPower(timetrace_Pout2, output='watt', direction='bw') )
            # default case
            else:
                timetrace   = tjk.get_trace(shot, fname_in=fname_data, 
                                            chName=chCfg[key][0])

            ylabel  = chCfg[key][3]

            # optionally, scale timetraces to physical units (instead of volts)
            if np.isfinite(chCfg[key][1]):
                timetrace *= chCfg[key][1]
            if key == 'plot_P2GHz_in':
                timetrace   = tjk.calc_2GHzPower(timetrace_Pin2,  output='watt', direction='fw')
            elif key == 'plot_P2GHz_out':
                timetrace   = tjk.calc_2GHzPower(timetrace_Pin2,  output='watt', direction='bw')
            elif key == 'plot_P8GHz_in':
                timetrace   = tjk.calc_8GHzPower(timetrace,  direction='fw')*1e-3
            elif key == 'plot_interf':
                # correct for drift
                # correct for offset
                # calculate actual electron plasma density
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
                if timetraces_options['interf_offset_correct']:
                    offset_end      = np.mean(timetrace[(-1*n_pts_offset):])
                    timetrace      += -1*offset_end 
                if timetraces_options['interf_calc_ne']:
                    # TODO: for 'Interferometer (Mueller)' and 'Interferometer Phase' the
                    #       scaling factor is 3.883e17 until the damage and repair by e.ho
                    #       in summer 2022, then it was changed to half of that.
                    #       for 'Density (old)' and befor the factor is 6.7e16
                    if shot >= 13032:
                        timetrace_ne    *= 3.883/2.#e17
                    else:
                        timetrace_ne    *= 3.883#e17
                    ylabel = r'$\bar{n}_e$ in $10^{17}\,\mathrm{m}^{-3}$'

            # optionally set y-range
            if key == 'plot_Tcoil':
                ax.set_ylim(20, 110)

            ax.plot(time, timetrace)
            ax.set_ylabel(ylabel)

            # plot shot number as title on top
            if plot_count == 1:
                ax.set_title('#{0}'.format(shot))

            plot_count  += 1

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
        'plot_B0'               : 1,
        'plot_Tcoil'            : 0,
        'plot_P2GHz_abs'        : 1,
        'plot_P8GHz_in'         : 0,
        'plot_interf'           : 1,
        'interf_drift_correct'  : 0,
        'interf_offset_correct' : 0,
        'interf_calc_ne'        : 0,
        'plot_BoloSum'          : 0,
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
plot_B0_var                 = tk.IntVar(value=timetraces_options['plot_B0'])
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
                                                 "plot_B0",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
plot_B0_checkbutton.grid(row=3, column=1, sticky=tk.W, padx=5)
# checkbutton for plotting timetrace of T_coil
plot_Tcoil_var              = tk.IntVar(value=timetraces_options['plot_Tcoil'])
plot_Tcoil_checkbutton      = tk.Checkbutton(side_frame_inner, 
                                             text="include T_coil",
                                             variable=plot_Tcoil_var,
                                             onvalue=1, offvalue=0,
                                             state=tk.NORMAL,
                                             command=lambda: checkbutton_clicked(
                                                 plot_Tcoil_var,
                                                 "plot_Tcoil",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
plot_Tcoil_checkbutton.grid(row=4, column=1, sticky=tk.W, padx=5)
# checkbutton for plotting P_abs2.45GHz timetrace
plot_P2GHzAbs_var           = tk.IntVar(value=timetraces_options['plot_P2GHz_abs'])
plot_P2GHzAbs_checkbutton   = tk.Checkbutton(side_frame_inner, 
                                             text="include P_abs2.45GHz",
                                             variable=plot_P2GHzAbs_var,
                                             onvalue=1, offvalue=0,
                                             state=tk.NORMAL,
                                             command=lambda: checkbutton_clicked(
                                                 plot_P2GHzAbs_var,
                                                 "plot_P2GHz_abs",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
plot_P2GHzAbs_checkbutton.grid(row=5, column=1, sticky=tk.W, padx=5)
# checkbutton for ingoing 8 GHz measured via Kasparek diode
P8GHz_in_var    = tk.IntVar()
P8GHz_in_check  = tk.Checkbutton(side_frame_inner,
                                 text="include P_in8GHz",
                                 variable=P8GHz_in_var,
                                 state=tk.NORMAL,
                                 command=lambda: checkbutton_clicked(
                                    P8GHz_in_var,
                                    "plot_P8GHz_in",
                                    timetraces_options,
                                    status_label)
                                 )
P8GHz_in_check.grid(row=6, column=1, sticky=tk.W, padx=5)
# checkbutton for plotting interferometer timetrace
plot_interf_var             = tk.IntVar(value=timetraces_options['plot_interf'])
plot_interf_checkbutton     = tk.Checkbutton(side_frame_inner, 
                                             text="include interferometer",
                                             variable=plot_interf_var,
                                             onvalue=1, offvalue=0,
                                             state=tk.NORMAL,
                                             command=lambda: checkbutton_clicked(
                                                 plot_interf_var,
                                                 "plot_interf",        # NOTE: must be same as dictionary key 
                                                 timetraces_options,
                                                 status_label)
                                            )
plot_interf_checkbutton.grid(row=7, column=1, sticky=tk.W, padx=5)
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
interf_drift_checkbutton.grid(row=8, column=1, sticky=tk.W, padx=5)
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
interf_neCalc_checkbutton.grid(row=9, column=1, sticky=tk.W, padx=5)
# checkbutton for correction for offset at end
interf_offsetCorr_var   = tk.IntVar()
interf_offsetCorr_check = tk.Checkbutton(side_frame_inner,
                                         text="correct offset",
                                         variable=interf_offsetCorr_var,
                                         state=tk.NORMAL,
                                         command=lambda: checkbutton_clicked(
                                             interf_offsetCorr_var,
                                             "interf_offset_correct",
                                             timetraces_options,
                                             status_label)
                                         )
interf_offsetCorr_check.grid(row=10, column=1, sticky=tk.W, padx=5)
# checkbutton for including the Bolometer sum channel
boloSum_var     = tk.IntVar()
boloSum_check   = tk.Checkbutton(side_frame_inner,
                                 text="include Bolo_sum",
                                 variable=boloSum_var,
                                 state=tk.DISABLED,
                                 command=lambda: checkbutton_clicked(
                                     boloSum_var,
                                     "plot_BoloSum",
                                     timetraces_options,
                                     status_label)
                                 )
boloSum_check.grid(row=11, column=1, sticky=tk.W, padx=5)



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

