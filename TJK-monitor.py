# coding=utf-8

__author__      = 'Alf Köhn-Seemann'
__email__       = 'koehn@igvp.uni-stuttgart.de'
__copyright__   = 'University of Stuttgart'
__license__     = 'MIT'


# import standard modules
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os.path
import re
import socket


def get_shot_path( shot ):
#{{{
    """
    Return the full path of a certain shot.

    Parameters
    ----------
    shot : int
        Shot number

    Returns
    -------
    str
        Full path to shot folder, returns errValue (-1) if not found
    """

    errValue    = -1

    if isinstance(shot, str):
        print('get_shot_path: warning, argument <shot> should be int, is string')
        print('               will be converted to int, shot = ', shot)
        print('               might trigger some side effects')

    possible_folders    = [ 
                            '/data6/', 
                            '/data5/', 
                            '/data4/', 
                            '/data3/', 
                            '/data2/', 
                            '/data1/' 
                          ]

    for prePath in possible_folders:
        shot_path   = '{0}/shot{1:d}/'.format( prePath, shot )
        if os.path.isdir(shot_path):
            break

    if not os.path.isdir(shot_path):
        shot_path   = errValue

    return shot_path

#}}}


def get_gas( shot ):
#{{{
    """
    Return the gas used during a certain shot.

    This should be changed such that the gas is read from a file where this
    information is stored. This would be much easier to maintain than compared
    to always change a code (as is the current situation).

    Parameters
    ----------
    shot : int
        Shot number

    Returns
    -------
    str
        Gas abbreviated as in the periodic table of the elements 
    """

    if shot == 6464:
        gas = 'He'
    elif shot == 6465:
        gas = 'He'
    elif shot == 6466:
        gas = 'He'
    elif shot == 6467:
        gas = 'He'
    elif shot == 6477:
        gas = 'He'
    elif shot == 6478:
        gas = 'He'
    elif shot == 6479:
        gas = 'He'
    elif shot == 6480:
        gas = 'He'
    elif shot == 6481:
        gas = 'He'
    elif ((shot >= 12838) and (shot <= 12887)):
        gas = 'He'
    else:
        gas = ''

    return gas
#}}}


def get_header( shot, fname_in='', silent=False ):
    #{{{
    """
    Returns the header from the file saved by tjk-monitor.vi.

    Copied from tjk_monitor.pro on 26.09.2018.

    Parameters
    ----------
    shot : int
        Shot number
    fname_in : str, optional
        Allows to optionally specify a filename explicitely (if it would not 
        be located at the default locations, for example).
    silent : bool, optional
        If True some useful (?) output will be printed to console.

    Returns
    -------
    """

    if not silent:
        print( 'get_header' )

    # value to return in case of error
    errValue = -1

    # headers were introduced with shot 5874
    if shot <= 5873:
        print( '    ATTENTION: this shot was recorder with an old version of tjk-monitor' )
        print( '               no header was saved in data files' )
        print( '               header information was manually added afterwards by A. Koehn' )

        # STILL NEEDS TO BE IMPLEMENTED
        # get_TJKMonitor_chInfo(shot)

        return errValue

    # read header of tjk-monitor (or tjk-multimeter, or whatever it might be called by now) file
    # filename of tjk-monitor(/-multimeter) file
    if len(fname_in) == 0:
        path_data   = get_shot_path( shot )
        # if shot path is not found, use local active folder
        if (path_data == -1):
            path_data  = ''
        fname_data  = path_data+'interferometer/shot{0:d}.dat'.format( shot )
    else:
        fname_data  = fname_in
    # number of lines that include the header
    n_headerlines = 4
    # read file line-by-line and only keep last line as this contains the channel names
    f = open( fname_data, 'r' )
    for ii in range(n_headerlines):
        ### the ',' at the end erases the 'carriage return' ('CR')
        channel_names = f.readline(),

    # split header string into list, using tab character as separator
#    channel_names = re.split( r'\t+', channel_names[0].rstrip( '\t') )
    channel_names = re.split( r'\t+', channel_names[0] )

    return channel_names
#}}}


def get_column_nr( shot, str2find, fname_in='', silent=False):
    #{{{
    """
    Return the column number of a specified time trace from tjk-monitor.vi file

    Copied from tjk_monitor.pro on 26.09.2018.

    Parameters
    ----------
    shot : int
        Shot number
    str2find : str
        String used to identify the column number. 
    fname_in : str, optional
        Allows to optionally specify a filename explicitely (if it would not 
        be located at the default locations, for example).
    silent : bool, optional
        If True some useful (?) output will be printed to console.

    Returns
    -------
    """

    if not silent:
        print( 'get_column_nr' )

    # value to return in case of error
    errValue = -1

    # get header of the tjk-multimeter file
    strArr2search = get_header( shot, fname_in=fname_in, silent=silent )

    # search header for string str2find
    if str2find in strArr2search:
        str_id = strArr2search.index( str2find )
    else:
        print( '    ERROR: <{0}> not in header of tjk-monitor file' )
        return errValue

    if not silent:
        print( '    shot={0:d}, channel name={1}, channel number found={2:d}'.format( shot, str2find, str_id ))

    return str_id

    #}}}


def get_trace( shot, fname_in='', chName='', chNr=None, silent=False ):
    #{{{
    """
    Returns the time trace of a single channel from a single shot.

    Copied from tjk_monitor.pro on 26.09.2018, adapted later.

    Parameters
    ----------
    shot : int
        Shot number
    fname_in : str, optional
        Allows to optionally specify a filename explicitely (if it would not 
        be located at the default locations, for example).
    chName : str, optional
    chNr : int, optional
    silent : bool, optional
        If True some useful (?) output will be printed to console.
    Returns
    -------

    """

    if not silent:
        print( 'get_trace' )

    # value to return in case of error
    errValue = 0

    # check if keywords are properly set
    ## check if both channel name and channel number are set
    if (len(chName)>0) and (chNr!=None):
        print( '    ERROR: both, channel name and number were set' )
        print( '           only one is allowed, will exit now' )
        return errValue
    ## check if both, channel name and channel number are not set
    if (len(chName)==0) and (chNr==None):
        print( '    ERROR: channel name or number need to be set' )
        print( '           will exit now' )
        return errValue

    # filename of time trace file
    if len(fname_in) == 0:
        path_data   = get_shot_path( shot )
        # if shot path is not found, use local active folder
        if (path_data == -1):
            path_data  = ''
        fname_data  = path_data+'interferometer/shot{0:d}.dat'.format( shot )
    else:
        fname_data  = fname_in

    # check if file exists
    if not os.path.isfile( fname_data ):
        print( '    ERROR: file <{0}> does not exist'.format( fname_data ))
        return errValue

    # get channel number if channel name is set
    if len(chName) > 0:
        chNr = get_column_nr( shot, chName, fname_in=fname_in )
        if not silent:
            print( '    shot={0:d}, channel name={1}, channel number={2:d}'.format( shot, chName, chNr ) )

    # read data
    time_trace = np.loadtxt( fname_data, skiprows=4)

    if not silent:
        print( '    time traces successfully read from file into memory, shape={0}'.format( time_trace.shape ) )

    return time_trace[:,chNr]
    #}}}


def calc_real_pressure( pressure, gas ):
#{{{
    """
    Calculates the real pressure for the PKR-device.

    Correction values are from the manual.
    (Function originally from little_helper.pro from 26.09.2018)

    Parameters
    ----------
    pressure : float
        Neutral gas pressure.
    gas : str
        Gas abbreviated as in the periodic table of the elements.
        
    Returns
    -------
    float
        Corrected neutral gas pressure.

    """

    if gas == 'H':
        corr = 2.4
    elif gas == 'D':
        print( '    you have choosen deuterium as gas, no calibration factor exists for this gas' )
        print( '    the same factor as for hydrogren will be used' )
        corr = 2.4
    elif gas == 'He':
        corr =5.9
    elif gas == 'Ne':
        corr =4.1
    elif gas == 'Ar':
        corr =.8
    elif gas == 'Kr':
        corr =.5
    elif gas == 'Xe':
        corr =.4
    else:
        print( '    you chose a gas for which no calibration factor exists' )
        print( '    the input value will be returned without a change' )
        corr = 1.

    p_eff = corr*pressure

    return p_eff
#}}}


def get_pressure( shot, fname_in='', silent=True ):
    #{{{
    """
    This function returns the real pressure before plasma is started.

    Returns pressure in units of Pascale.
    Originally from tjk_monitor.pro from 26.09.2018, adapted later.

    Parameters
    ----------
    shot : int
        Shot number
    fname_in : str, optional
        Allows to optionally specify a filename explicitely (if it would not 
        be located at the default locations, for example).
    silent : bool, optional
        If True some useful (?) output will be printed to console.

    Returns
    -------
    list
        List containing two floats.
    """

    # value to return in case of error
    errValue = -1

    # reproducibility error, absolute error is 30 % (according to manual)
    PKR_error = .05

    chName = 'Pressure'
    if (shot>=6464) and (shot <=6509):
        chName = 'slot1'

    if shot==6467:
        print( '    ATTENTION: no pressure time trace for recorded for this shot' )
        print( '               value will be set to what is written in Lab-book' )
        p0 = calc_real_pressure( 5e-3, gas=get_gas(shot) )
        return [ p0, PKR_error*p0 ]

    # get time traces
    pressure = get_trace( shot, fname_in=fname_in, chName=chName, silent=silent )

    # calculate mean of first 100 data points in time traces
    # (B0 and microwave should be turned off then)
    pts2avg = 100
    p0 = np.mean( pressure[ 0:pts2avg ] )

    # convert to mPa
    d = 9.33                # according to PKR261 manual
    p0 = 10.**(1.667*p0-d)

    # calculate real pressure (PKR261 is gas-sensitive)
    gas = get_gas( shot )
    p0  = calc_real_pressure( p0, gas )

    # calculate error according to Fehlerfortpflanzung
    ## standard deviation of mean of time trace
    p0_volt_err  = np.std( pressure[0:pts2avg] ) / np.sqrt( pts2avg -1 )
    ## p_err = dp/dU * U_err = 1.667*ln(10)*p0(U)*U_err
    p0_error     = 1.667*np.log(10.) * p0 * p0_volt_err
    ## relative error
    p0_error_rel = p0_error / p0

    # accuracy in pressure measurement is +-30% according to manual of PKR261
    # since this is not really the error of the values with respect to each other
    # it is not used; reproducibility is 5% error according to manual, this value is used
    return [ p0, (p0_error_rel+PKR_error)*p0 ]
#}}}


def get_pressure_labbook( shot, silent=True ):
#{{{
    """
    This function returns the neutral gas pressure from the lab book.

    Parameters
    ----------
    shot : int
        Shot number
    silent : bool, optional
        If True some useful (?) output will be printed to console.

    Returns
    -------
    numpy.array
        numpy.array containing two floats.

    """


    if shot == 12838:
        p0  = 3.
    elif shot == 12839:
        p0  = 2.
    elif shot == 12840:
        p0  = 1.57
    elif shot == 12841:
        p0  = 1.11
    elif shot == 12842:
        p0  = 1.04
    elif shot == 12843:
        p0  = 1.04
    elif shot == 12844:
        p0  = 1.04
    elif shot == 12845:
        p0  = 1.04
    elif shot == 12846:
        p0  = 1.04
    elif shot == 12847:
        p0  = 1.04
    elif shot == 12848:
        p0  = 1.04
    elif shot == 12849:
        p0  = 1.04
    elif shot == 12850:
        p0  = 1.99
    elif shot == 12868:
        p0  = 2.01
    elif shot == 12869:
        p0  = 2.01
    elif shot == 12874:
        p0  = 10.5
    elif shot == 12875:
        p0  = 7.94
    elif shot == 12876:
        p0  = 5.96
    elif shot == 12877:
        p0  = 10.1
    elif shot == 12878:
        p0  = 8.04
    elif shot == 12879:
        p0  = 6.00
    elif shot == 12880:
        p0  = 5.01
    elif shot == 12881:
        p0  = 4.04
    elif shot == 12882:
        p0  = 3.04
    elif shot == 12883:
        p0  = 4.73
    elif shot == 12884:
        p0  = 8.57
    elif shot == 12885:
        p0  = 10.5
    elif shot == 12886:
        p0  = 12.3
    elif shot == 12887:
        p0  = 14.3

    return np.array( [p0, .0] )
 
#}}}


def calc_2GHzPower( U_in, output='watt', direction='fw' ):
#{{{
    """
    This function calculates the power of the 2.45 GHz magnetron measured 
    at a directional coupler with two diodes.

    Parameters
    ----------
    U_in : numpy.array
        Time traces of the signal in voltage acquired with the TJK-monitor
        LabVIEW programm.
    output : str, optional
        Possible values are 'watt', 'dBm'.
    direction : str, optional
        Possible values are 'fw', 'bw'.

    Returns
    -------
    numpy.array
        numpy.array containing the time trace converted to power.

    """

    # positive values lead to NaN in the following calculations
    U_in[U_in>0]    = -1e-6

    # convert voltage signal (the time trace) from microwave diodes to dBm
    # diodes used: IDM211 from IBF electronic GmbH, formula is from data sheet
    signal_dBm  = 42.26782054007 + (-28.92407247331 - 42.26782054007) / ( 1. + (U_in / (-0.5508373840567) )**0.4255365582241 )

    # account for damping of directional coupler
    if direction == 'fw':
        signal_dBm  += 60.49
    elif direction == 'bw':
        signal_dBm  += 60.11

    if output == 'watt':
        signal2return   = 10**(signal_dBm/10.) * 1e-3
    elif output == 'dBm':
        signal2return   = signal_dBm

    return signal2return
#}}}


def calc_8GHzPower( U_in, direction='fw', old=False ):
#{{{
    """
    This function calculates the power of the 8 GHz klystron measured 
    at a directional coupler with a diode. 

    For the forward direction, this corresponds to the previously used IDL 
    function "kasparek_diode" written by Alf Köhn-Seemann (used the latest
    version from 2012-11-14 from little_helper.pro).

    Parameters
    ----------
    U_in : numpy.array
        Time traces of the signal in voltage acquired with the TJK-monitor
        LabVIEW programm.
    direction : str, optional
        Possible values are 'fw'. 'bw' is planned to be implemented later.
    old: bool, optional
        If true, old calibration made for the TWT is used.

    Returns
    -------
    numpy.array
        numpy.array containing the time trace converted to power in units
        of Watts.

    """

    # scale input signal to mV (calibration was done with mV)
    U_in *= 1e3

    # optionally, use old calibration from TWT, see p.34 of PhD-notes from AKS
    if old:
        a1  = .771523
        a2  = 4.97773
        a3  = 1.394

        P   = ( (U_in/a1)**2 * 1./a2 )**(1./a3)
    else:
        # use new calibration with Klystron, see p.144 of PD-notes from AKS
        a1  = 17.5637
        a2  = 0.332023
        a3  = 0.458919 

        P   = a1 * np.exp(a2 * np.abs(U_in)**a3)

    return P
#}}}


def get_lineAvgDensity( U_in, silent=True ):
    #{{{

    # correct for offset at the end of the time trace
    # assumes that tjk-monitor is running after plasma is turned off
    n_pts_offset    = 100
    offset_end      = U_in[(-1*n_pts_offset):]
    U_in           += -1*offset_end

    #}}}


def plot_timetraces( shot, fname_out='', 
                     silent=True ):
#{{{
    # idea: use dictionary for each diagnostics data stored via tjk-monitor
    #       which contains channel name in tjk-monitor, conversion factor,
    #       physical unit after applying conversion factor, comment,
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

    # number of timetraces to plot
    # will probably be changed as an optional keyword later
    n_traces    = 4

    data2plot   = ['B0', 'Pin2', 'neMueller', 'BoloSum']

    # get time axis and scale it to seconds
    time    = get_trace(shot, chName='Zeit [ms]')
    time   *= 1e-3

    n_rows  = n_traces
    n_cols  = 1
    # figsize is per default (width, height) in inches
    fig, axs    = plt.subplots( n_rows, n_cols, figsize=(8,8) )
    fig.suptitle('#{0}'.format(shot))

    # fig return value of plt.subplot has list of all axes objects
    for i, ax in enumerate(fig.axes):
        timetrace   = get_trace( shot, chName=chCfg[data2plot[i]][0], silent=silent)
        if np.isfinite(chCfg[data2plot[i]][1]):
            timetrace *= chCfg[data2plot[i]][1]
        ax.plot( time, timetrace )
        ax.set_ylabel( chCfg[data2plot[i]][3] )
    # add x-label only to bottom axes object
    ax.set_xlabel( 'time in s' )

    plt.show()
#}}}
    

def main():
#{{{
    print( 'This file contains some hopefully useful functions to handle the data acquired with the TJK-Monitor LabVIEW program' )

    # initialize parser for command line options
    parser  = argparse.ArgumentParser()
    # add optional arguments
    parser.add_argument( "-s", "--shot", type=int, default=13000, 
            help='Shot number' )
    # read all arguments from command line
    args    = parser.parse_args()

    shot    = args.shot

    # print info about shot
    print( "Shot number: {0}".format(shot) )

    plot_timetraces( shot, fname_out='', 
                     silent=True )
#}}}


if __name__ == '__main__':
    main()

