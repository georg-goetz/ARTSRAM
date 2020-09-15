import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
import sounddevice as sd
import scipy.io.wavfile as wav
import pathlib
import queue
import threading

import measurement_utils as utils
import measurement_params as parameters


class SweepMeasurementError(Exception):
    pass


class SweepMeasurement(object):
    def __init__(self, nfft, fs=48000, fstart=10, fstop=24000, timew=0, amplw=0, end_delay=0.4):
        self.logger = utils.init_logger('SweepMeasurement')

        self.fs = fs
        self.session_path = ''

        self.measurement_id = None

        self.recording_lock = threading.Lock()
        self.recording_blocks = []
        self.sweep_playback_complete = False

        sweep, deconv_filter, nsweep, pre_delay, post_delay = self.init_sweep(nfft, fstart, fstop, timew, amplw,
                                                                              end_delay)
        self.sweep = sweep
        self.deconv_filter = deconv_filter
        self.nsweep = nsweep
        self.pre_delay = pre_delay
        self.post_delay = post_delay

        self.calibration_factor = 1

    def set_session_path(self, session_path):
        self.session_path = session_path
        self.logger.info('Set the session path for the sweep recordings to \"{}\"'.format(session_path))

    def set_measurement_id(self, measurement_id):
        self.measurement_id = measurement_id
        self.logger.info('Set the measurement ID to \"{}\".'.format(measurement_id))

    def set_sweep_playback_complete(self, sweep_playback_complete):
        self.sweep_playback_complete = sweep_playback_complete
        self.logger.info('Switched the sweep_playback_complete flag to {}'.format(sweep_playback_complete))

    def get_audio_devices(self):
        this_os = utils.get_operating_system()
        if this_os == 'linux':
            devices = (parameters.SD_IN_LINUX, parameters.SD_OUT_LINUX)
        elif this_os == 'mac':
            devices = (parameters.SD_IN_MAC, parameters.SD_OUT_MAC)
        else:
            self.logger.error('Unsupported platform.')
            raise SystemExit('This platform is not supported yet.')

        return devices

    def play_sweep(self):
        devices = self.get_audio_devices()

        try:
            self.logger.info('Playing back sweep now.')
            sd.play(self.sweep, samplerate=self.fs, device=devices[1], blocking=True)
            self.logger.info('Sweep playback ended.')
        except ValueError as e:
            self.logger.error('The sweep playback was not successful, because there was a problem with the sound '
                              'device. Maybe check the sound-device names with sd.query_devices() and adjust them in '
                              'the measurement parameters.')
            raise SweepMeasurementError('The sweep playback was not successful, because there was a problem with the '
                                        'sound device. Maybe check the sound-device names with sd.query_devices() and '
                                        'adjust them in the measurement parameters.') from e

    def recording_callback(self, indata, frames, time, status):
        """
        This is called from a seperate thread for each audio block.
        :param indata: input buffer, as two-dimensional numpy.ndarray with one column per channel (i.e. with a shape of
            (frames, channels)) and with a data type specified by dtype.
        :param frames: number of frames to be processed by the stream callback. This is the same as the length of the
            input buffer
        :param time: The forth argument provides a CFFI structure with timestamps indicating the ADC capture time of the
            first sample in the input buffer (time.inputBufferAdcTime), and the time the callback was invoked
            (time.currentTime). These time values are expressed in seconds and are synchronised with the time base used
            by time for the associated stream.
        :param status: CallbackFlags instance indicating whether input and/or output buffers have been inserted or will
            be dropped to overcome underflow or overflow conditions.

        The 4 arguments need to be just like that for sounddevice.InputStream to work, compare:
        https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.InputStream
        """
        if status:
            self.logger.info(status)

        # block is added to the recording
        with self.recording_lock:
            self.recording_blocks.append(indata.copy())

    def record_until_stopped(self):
        devices = self.get_audio_devices()

        self.recording_blocks = []

        with sd.InputStream(samplerate=self.fs, device=devices[0], channels=4, callback=self.recording_callback):
            self.logger.info('Starting to record.')
            while not self.sweep_playback_complete:
                # do nothing, because the callback function does the work. we just have to wait until the sweep has
                # played entirely
                pass

        self.logger.info('Recording finished.')

    def conduct_measurement(self, playback=False):
        devices = self.get_audio_devices()
        try:
            if playback:
                # simultaneous playback and recording (only possible when both input and output device are operated by
                # the same computer
                recording = sd.playrec(self.sweep, samplerate=self.fs, device=devices, channels=4, blocking=True)
            else:
                # if no simultaneous playback is possible, allow some additional time (e.g. 2 seconds) in case the
                # server connection is very slowly
                recording_length = len(self.sweep) + 2 * self.fs
                recording = sd.rec(recording_length, samplerate=self.fs, device=devices[0], channels=4, blocking=True)
        except ValueError as e:
            self.logger.error('The measurement was not successful, because there was a problem with the sound device. '
                              'Maybe check the sound-device names with sd.query_devices() and adjust them in the '
                              'measurement parameters.')
            raise SweepMeasurementError('The measurement was not successful, because there was a problem with the '
                                        'sound device. Maybe check the sound-device names with sd.query_devices() and '
                                        'adjust them in the measurement parameters.') from e

        self.recording2rirs(recording)

    def blockwiserecording2rirs(self):
        recording = np.concatenate(self.recording_blocks, axis=0)

        # pad the recording to an integer number of seconds (fft runs faster for lengths of power of 2 and apparently
        # in numpy also for multiples of 48000, which seemed to be even faster than for 'normal' even numbers?)
        n_secs = int(np.floor(len(recording)/48000))
        recording = np.append(recording, np.zeros(((n_secs+1)*48000-len(recording), 4)), 0)
        self.logger.info('Converted block-wise recording to a single recording with shape {}.'.format(recording.shape))
        self.recording2rirs(recording)

    def recording2rirs(self, recording):
        # The first measurement should be conducted from positions exhibiting the smallest possible distance between
        # source and receiver. From this measurement, the microphone recordings are normalized such that their amplitude
        # is at most 0.9 when an amplitude as high as the maximum amplitude of the first measurement is obtained. This
        # effectively ensures a high level of the recordings and it should prevent clipping
        if self.measurement_id == 1:
            max_val_recording = np.max(np.abs(recording))
            if max_val_recording == 1:
                self.logger.error('The recording seems to clip. Please reduce the gain of the microphone.')
                raise SystemExit('The recording seems to clip. Please reduce the gain of the microphone.')
            else:
                self.calibration_factor = 0.9 / max_val_recording
                self.logger.info('Set calibration factor to {}.'.format(self.calibration_factor))

        # Do normalization
        recording = recording * self.calibration_factor
        if np.max(np.abs(recording)) > 1:
            self.logger.warning('The microphone recording after normalization should have no values higher than 1! '
                                'Clipping may occur.')

        # Deconvolve sweep for all channels
        rirs = np.zeros_like(recording)
        for cIdx, channel in enumerate(recording.T):
            self.logger.info('Deconvolving RIR {}.'.format(cIdx))
            # window the fluctuations before and after the actual sweep
            w = sig.windows.hann(2 * self.pre_delay)
            channel[0:self.pre_delay] = channel[0:self.pre_delay] * w[0:self.pre_delay]
            w = sig.windows.hann(2 * self.post_delay)
            channel[-self.post_delay:None] = channel[-self.post_delay:None] * w[self.post_delay:None]

            # deconvolve
            rirs[:, cIdx] = self.deconvolve_sweep(channel)
        self.logger.info('RIRs deconvolved.')

        # Cut RIRs to maximal length
        rirs = rirs[:parameters.MAX_RIR_LENGTH * self.fs, :]

        # Save to wav file
        year, month, day = utils.get_current_date()
        hour, minute, second = utils.get_current_time()
        filename = '{:05}_{}_{:02}_{:02}_{:02}_{:02}_{:02}_RIRs.wav'.format(self.measurement_id, year, month, day,
                                                                            hour, minute, second)
        path = str(pathlib.Path(self.session_path, filename))
        rec_path = str(pathlib.Path(self.session_path, 'rec_' + filename))
        wav.write(rec_path, self.fs, recording)
        wav.write(path, self.fs, rirs)

    def init_sweep(self, nfft, fstart=10, fstop=24000, timew=0, amplw=0, end_delay=0.4):
        """
        Original MATLAB-based code by Juha Merimaa, 2003.
        Python port by Georg Götz, 2020.

        Creates a logarithmic (or modified logarithmic) sweep excitation signal for
        impulse measurement purposes. Frequency domain sweep generation is used to allow
        more control on the sweep properties. As a default the time domain sweep will
        have a (nearly) constant amplitude.

        :param nfft: Number of samples in one sweep. For faster operation use a power of two.
            Nfft must to be higher than the length of the impulse response being measured
            in order to avoid circular wrapping of the response when averaging results of
            several sweep repetitions.
        :param fstart: limiting the frequency range of the sweep excitation
        :param fstop: limiting the frequency range of the sweep excitation
        :param timew: Sweep magnitude spectrum weighting that will affect the sweep rate of a constant amplitude sweep.
        :param amplw: Sweep magnitude spectrum weighting applied as amplitude control of the sweep signal.
        :param end_delay: Defines the fraction of zero samples in the end of a single period of a sweep signal. The
        zeros are needed to capture the full response when a single sweep is used. When averaging repeated sweeps it is
        best to keep this parameter zero. Defaults: when nrep = 1: 0.4, otherwise: 0.
        :return: s: sweep, H: deconvolution filter, nsweep: number of samples in sweep, pre_delay: delay before sweep,
        post_delay: delay after sweep
        """
        if self.fs != 48000 and fstop == 24000:
            fstop = self.fs / 2

        # allow some time for fluctuations before and after the actual sweep within the final excitation signal
        fstart = max(fstart, self.fs / (2 * nfft))
        pre_delay = int(np.ceil(max(self.fs / fstart, nfft / 200)))
        if pre_delay > nfft / 10:
            pre_delay = int(np.ceil(nfft / 10))
        post_delay = int(np.ceil(max(self.fs / fstop, nfft / 200)))
        if post_delay > nfft / 10:
            post_delay = int(np.ceil(nfft / 10))

        # update number of samples in actual sweep due to previous steps
        nsweep = round((1 - end_delay) * nfft) - pre_delay - post_delay

        # transform into seconds
        sweep_sec = nsweep / self.fs
        pre_delay_sec = pre_delay / self.fs

        # from here on use a double length time window to prevent time domain artifacts from wrapping to the sweep
        # signal (note: this makes nfft always even!)
        n_half_fft = nfft + 1  # up to and including Nyquist
        nfft = 2 * nfft
        f = np.linspace(0, n_half_fft - 1, n_half_fft) * self.fs / nfft

        # construct a pink magnitude spectrum
        H = np.concatenate(([fstart / f[1]], np.sqrt(fstart / f[1:n_half_fft])))

        # frequency control options that will shape the time evolutions of the sweep: highpass filtering
        if fstart > self.fs / nfft:
            b_hp, a_hp = sig.butter(N=2, Wn=2 * fstart / self.fs, btype='highpass')
            __, h_hp = sig.freqz(b_hp, a_hp, 2 * np.pi * f / self.fs)
            H = H * np.abs(h_hp)
        # lowpass filtering
        if fstop < self.fs / 2:
            b_lp, a_lp = sig.butter(N=2, Wn=2 * fstop / self.fs)
            __, h_lp = sig.freqz(b_lp, a_lp, 2 * np.pi * f / self.fs)
            H = H * np.abs(h_lp)
        # user defined spectral weighting
        if timew:
            H = H * timew

        # calculate group delay
        C = sweep_sec / sum(np.square(H))
        tg = C * np.cumsum(np.square(H))
        tg = tg + pre_delay_sec

        # calculate phase
        ph = -2 * np.pi * self.fs / nfft * np.cumsum(tg)

        # force the phase to zero at Nyquist
        ph = ph - (f / f[n_half_fft - 1]) * (ph[n_half_fft - 1] % (2 * np.pi))

        # optional spectral weighting controlling the amplitude of the sweep
        if amplw:
            H = H * amplw

        # create double-sided spectrum
        H = H * np.exp(1j * ph)
        H = np.concatenate((H, np.conj(H[n_half_fft - 2:0:-1])))

        # convert to time domain
        s = np.real(np.fft.ifft(H))

        # window the fluctuations before and after the actual sweep
        w = sig.windows.hann(2 * pre_delay)
        s[0:pre_delay] = s[0:pre_delay] * w[0:pre_delay]
        stop_ind = nsweep + pre_delay
        w = sig.windows.hann(2 * post_delay)
        s[stop_ind:stop_ind + post_delay] = s[stop_ind:stop_ind + post_delay] * w[post_delay:2 * post_delay]
        s[stop_ind + post_delay:nfft] = 0

        # back to the user defined nfft
        nfft = int(nfft / 2)
        s = s[0:nfft]

        # normalize the amplitude and create the repetitions
        normfact = 1.02 * max(abs(s))
        s = s / normfact

        H = 1 / np.fft.fft(s[0:nfft])
        f = np.linspace(0, nfft - 1, nfft) * self.fs / nfft

        # calculate a new reference spectrum without the bandpass filtering (in order not to amplify noise by the
        # inverse of the sweep energy far outside the sweep band)
        if fstart > self.fs / nfft:
            __, h_hp = sig.freqz(b_hp, a_hp, 2 * np.pi * f / self.fs)
            H = H * np.abs(h_hp)
        if fstop < self.fs / 2:
            __, h_lp = sig.freqz(b_lp, a_lp, 2 * np.pi * f / self.fs)
            H = H * np.abs(h_lp)

        return s, H, nsweep, pre_delay, post_delay

    def init_legacy_sweep(self, f1, f2, sweep_length):
        # init the excitation sweep
        w1 = f1 * 2 * np.pi
        w2 = f2 * 2 * np.pi
        t = np.linspace(0, sweep_length, sweep_length * self.fs + 1)
        sweep = np.sin(
            ((w1 * sweep_length) / np.log(w2 / w1)) * (np.exp((t / sweep_length) * np.log(w2 / w1)) - 1))

        # init the deconvolution filter
        temp = np.flip(self.sweep)  # time reversal
        weight_6db = 1 / (
            np.exp(t * np.log(w2 / w1) / sweep_length))  # get this from "instantaneous" energy consideration
        deconv_filter = temp * weight_6db

        return sweep, deconv_filter

    def deconvolve_sweep(self, measurement):
        # if the peak of the IR is in the last half of the IR, then there is something wrong, possibly because
        # of a synchronization mismatch between source and receiver socket. Then it is necessary to pad zeros to the
        # measurement until it is in the first half.
        len_measurement = len(measurement)
        max_shifts = round((len_measurement / 2) / (self.fs / 5))
        n_shifts = 0
        ir = None

        while n_shifts < max_shifts:
            if len_measurement > len(self.deconv_filter):
                # zero pad the deconvolution filter if the measurement is longer than the original sweep
                self.logger.debug('Pad zeros to deconvolution filter, because measurement is longer.')
                deconv_filter = np.fft.ifft(self.deconv_filter)
                n_pad = len_measurement - len(deconv_filter)
                deconv_filter = np.append(np.zeros(n_pad), deconv_filter)
                deconv_filter_f = np.fft.fft(deconv_filter)
            else:
                deconv_filter_f = self.deconv_filter

            self.logger.debug('Deconvolving the sweep in frequency domain.')
            ir = np.real(np.fft.ifft(np.fft.fft(measurement) * deconv_filter_f))

            self.logger.debug('Finding the peak.')
            this_propagation_delay = np.argmax(np.abs(ir))
            if this_propagation_delay > len(measurement) / 2:
                # if the peak of the IR is in the last half of the IR, then there is something wrong, possibly because
                # of a synchronization mismatch between source and receiver socket.
                self.logger.warning('Peak is in second half of impulse response. I will pad zeros before the '
                                    'measurement until it is in the first half.')
                measurement = np.append(np.zeros(round(self.fs / 5)), measurement)
                measurement = measurement[:len_measurement]
                n_shifts += 1
            else:
                # peak is in the first half of the IR, this is usually ok
                return ir

        self.logger.error('Could not find a proper IR, but I will return my current guess either way.')
        return ir
