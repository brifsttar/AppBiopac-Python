"""
Credit to @esdalmaijer for initial basis for code at:
https://github.com/esdalmaijer/MPy150

Credit to @rmarkello for updated version in rtpeaks:
https://github.com/rmarkello/rtpeaks

Credit to @rderollepot for adding digital channels support
"""

from __future__ import print_function, division, absolute_import
try:
    from ctypes import windll, c_int, c_double, byref
    from ctypes.wintypes import DWORD
except ImportError:
    pass
import os


def do_nothing():
    """Does absolutely nothing
    """
    pass


def get_returncode(returncode):
    """
    Checks return codes from BIOPAC device

    Parameters
    ----------
    returncode : int
        Code returned by call to BIOPAC

    Returns
    -------
    str
        Plain-text "translation" of `returncode`
    """

    errors = ['MPSUCCESS', 'MPDRVERR', 'MPDLLBUSY',
              'MPINVPARA', 'MPNOTCON', 'MPREADY',
              'MPWPRETRIG', 'MPWTRIG', 'MPBUSY',
              'MPNOACTCH', 'MPCOMERR', 'MPINVTYPE',
              'MPNOTINNET', 'MPSMPLDLERR', 'MPMEMALLOCERR',
              'MPSOCKERR', 'MPUNDRFLOW', 'MPPRESETERR',
              'MPPARSERERR']
    error_codes = dict(enumerate(errors, 1))
    try:
        e = error_codes[returncode]
    except:
        e = returncode

    return e


def setup_biopac(dic):
    """
    Does most of the set up for the BIOPAC

    Connects to BIOPAC MP device, sets sample rate, sets acquisition channels,
    and starts acquisiton daemon

    Parameters
    ----------
    dic : multiprocessing.manager.Dict
        dll_dir : str
            Directory where `mpdev.dll` can be found
        sampletime : float
            Number of milliseconds per sample
        channels : list
            From which channels to record data
        digital_channels : list
            From which digital channels to record data
        connected : boolean
            Whether process was able to successfully connect to the BIOPAC and
            start relevant acquisition daemon
    """

    # load required library
    try: mpdev = windll.LoadLibrary('mpdev.dll')
    except:
        f = os.path.join(dic['dll_dir'], 'mpdev.dll')
        try: mpdev = windll.LoadLibrary(f)
        except: raise Exception('Could not load mpdev.dll')

    # connect to BIOPAC
    try: result = mpdev.connectMPDev(c_int(103), c_int(11), b'auto')
    except: result = 0
    result = get_returncode(result)
    if result != "MPSUCCESS":
        try: result = mpdev.connectMPDev(c_int(101), c_int(11), b'auto')
        except: result = 0
        result = get_returncode(result)
        if result != "MPSUCCESS":
            raise Exception("Failed to connect to BIOPAC: {}".format(result))

    # set sampling rate
    try: result = mpdev.setSampleRate(c_double(dic['sampletime']))
    except: result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to set samplerate: {}'.format(result))

    # set acquisition channels
    chnls = [0] * 16
    for x in dic['channels']: chnls[x - 1] = 1
    chnls = (c_int * len(chnls))(*chnls)

    try: result = mpdev.setAcqChannels(byref(chnls))
    except: result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to set channels to acquire: {}'.format(result))

    # set digital acquisition channels
    digit_chnls = [0] * 16
    for x in dic['digital_channels']: digit_chnls[x - 1] = 1
    digit_chnls = (c_int * len(digit_chnls))(*digit_chnls)

    try:
        result = mpdev.setDigitalAcqChannels(byref(digit_chnls))
    except:
        result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to set digital channels to acquire: {}'.format(result))

    # start acquisition daemon
    try: result = mpdev.startMPAcqDaemon()
    except: result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to start acq daemon: {}'.format(result))

    # start acquisition
    try: result = mpdev.startAcquisition()
    except: result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to start data acquisition: {}'.format(result))

    dic['connected'] = True

    return mpdev


def shutdown_biopac(dll):
    """
    Stop acquisition daemon and disconnect from the BIOPAC

    Parameters
    ----------
    dll : WinDLL
        Loaded from `mpdev.dll`
    """

    # stop acquisition
    try: result = dll.stopAcquisition()
    except: result = 'failed to call stopAcquisition'
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to stop data acquisition: {}'.format(result))

    # close connection
    try: result = dll.disconnectMPDev()
    except: result = 'failed to call disconnectMPDev'
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to disconnect from BIOPAC: {}'.format(result))


def receive_data(dll, channels, digital_channels):
    """
    Receives a datapoint from the BIOPAC

    Parameters
    ----------
    dll : WinDLL
        Loaded from `mpdev.dll`
    channels : (1 x 16) array_like
        Specify whether to record from a given channel [on=1, off=0]
    """

    num_points, read = len(channels)+len(digital_channels), DWORD(0)
    data = [0] * num_points
    data = (c_double * len(data))(*data)
    try:
        result = dll.receiveMPData(byref(data), DWORD(num_points), byref(read))
    except:
        result = 0
    result = get_returncode(result)
    if result != 'MPSUCCESS':
        raise Exception('Failed to obtain a sample: {}'.format(result))

    return data
