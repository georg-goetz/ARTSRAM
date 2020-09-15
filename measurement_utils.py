import logging
import logging.handlers
import threading
import time
import sys
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib

import measurement_params as parameters
import logging_server as logs


def initialize_session_env():
    year, month, day = get_current_date()

    s_name = input('Please enter a session name.\n')
    s_name = '{}_{:02}_{:02}_{}'.format(year, month, day, s_name.lower())
    s_path = pathlib.Path('..', '..', 'measurements', s_name)

    overwrite = False
    try:
        s_path.mkdir(parents=True)

        add_logging_file_handler(s_path, s_name)

        _logger.info('Creating the session directory \"{}\"'.format(s_path))
    except FileExistsError:
        _logger.warning('There is already a directory with the name \"{}\"'.format(s_path))
        cont_prompt = input('Should the script be continued? This might overwrite previously measured data. (y/n)\n')

        if cont_prompt == 'y':
            overwrite = True
            s_path.mkdir(parents=True, exist_ok=True)

            add_logging_file_handler(s_path, s_name)

            _logger.warning('Overwrote the session directory \"{}\" as requested by the user.'.format(s_path))
        elif cont_prompt == 'n':
            _logger.info('Exiting the script, because the user chose to not overwrite the existing directory.')
            raise SystemExit('You did not want to overwrite data. Good choice. Therefore this script will end now.')
        else:
            _logger.error('Invalid user answer.')
            raise SystemExit('Your answer must be either \"y\" or \"n\".')

    return s_name, overwrite


def init_metadata_frame():
    df = pd.DataFrame(columns=['Measurement_ID', 'Timestamp', 'Position_Receiver', 'Orientation_Receiver',
                               'Position_Source', 'Orientation_Source'])
    return df


def add_measurement_to_frame(frame, measurement_id, localtime_obj, position_rcv, position_src):
    # Convert time object to a format that can be easily handled in pandas
    ts = pd.Timestamp(year=localtime_obj.tm_year, month=localtime_obj.tm_mon, day=localtime_obj.tm_mday,
                      hour=localtime_obj.tm_hour, minute=localtime_obj.tm_min, second=localtime_obj.tm_sec)

    # Convert measurement ID to string
    measurement_id = '{:05}'.format(measurement_id)

    # Store data into pandas frame
    frame = frame.append({'Measurement_ID': measurement_id, 'Timestamp': ts,
                          'Position_Receiver': position_rcv.position, 'Orientation_Receiver': position_rcv.orientation,
                          'Position_Source': position_src.position, 'Orientation_Source': position_src.orientation},
                         ignore_index=True)
    return frame


def save_metadata(frame, session_name):
    filename = str(pathlib.Path('..', '..', 'measurements', session_name, '{}_metadata.csv'.format(session_name)))
    frame.to_csv(filename, index=False)


def add_logging_file_handler(m_path, m_name):
    logfile_name = str(pathlib.Path(m_path, '{}_log.log'.format(m_name)))
    logger_file_handler = logging.FileHandler(filename=logfile_name, mode='a')
    logger_file_handler.setFormatter(logging.Formatter(parameters.LOGGING_FORMAT))
    logger_file_handler.setLevel(parameters.LOGGING_LEVEL)
    logging.getLogger('').addHandler(logger_file_handler)


def start_logging_server():
    logging_server = logs.LoggingServer()
    logging_server_thread = threading.Thread(target=logging_server.serve_forever)
    logging_server_thread.daemon = True
    logging_server_thread.start()
    return logging_server


def init_logger(logger_name, add_logserver_handler=True):
    # initialize logger that can communicate via TCP with the client
    logger = logging.getLogger(logger_name)
    logger.setLevel(parameters.LOGGING_LEVEL)

    if add_logserver_handler:
        socket_handler = logging.handlers.SocketHandler(parameters.IP_MAIN, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socket_handler)
    return logger


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    return logger


def get_current_localtime_obj():
    time_obj = time.localtime()
    return time_obj


def get_current_date():
    time_struct = time.localtime()
    year = time_struct.tm_year
    month = time_struct.tm_mon
    day = time_struct.tm_mday

    return year, month, day


def get_current_time():
    time_struct = time.localtime()
    hour = time_struct.tm_hour
    minute = time_struct.tm_min
    second = time_struct.tm_sec

    return hour, minute, second


def get_operating_system():
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        this_os = 'linux'
    elif sys.platform.startswith('darwin'):
        this_os = 'mac'
    else:
        _logger.error('Unsupported platform.')
        raise SystemExit('This platform is not supported yet.')

    return this_os


def plot_spectrogram(signal, fs=48000):
    f, t, spec = sig.spectrogram(signal, fs)
    plt.pcolormesh(t, f, spec)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


def plot_spectrum(signal, fs=48000):
    n_fft = len(signal)
    signal_f = np.fft.fft(signal)
    f = np.fft.fftfreq(n_fft) * fs
    f = f[0:int(n_fft/2)-1]

    signal_magn_spec = 20*np.log10(np.abs(signal_f[0:int(n_fft/2)-1]))
    plt.semilogx(f, signal_magn_spec)
    plt.xlim((50, 20000))


def get_first_channel_wav_file(filename):
    __, all_channels = wav.read(filename)
    first_channel = all_channels[:, 0]
    return first_channel


logging.basicConfig(format=parameters.LOGGING_FORMAT)
_logger = init_logger('MeasurementUtils')
