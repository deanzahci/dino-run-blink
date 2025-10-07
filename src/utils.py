import logging

import numpy as np
from pylsl import StreamInlet, resolve_streams
from scipy.signal import butter, iirnotch, filtfilt

from config import (
    FS,
    BANDPASS_HIGH_CUT,
    BANDPASS_LOW_CUT,
    BANDPASS_ORDER,
    RMS_WINDOW_SIZE,
    NOTCH_TARGET_FREQ,
    NOTCH_QUALITY_FACTOR,
)


def stream():
    """
    Generator function that streams EOG data from LSL and yields buffers.

    This function connects to the LSL stream named "PetalStream_eeg", collects
    samples from AF7 and AF8 channels into a buffer, and yields the buffer when
    it reaches the specified RMS_WINDOW_SIZE.

    Yields:
        np.ndarray: A 2D array of shape (RMS_WINDOW_SIZE, 2) containing AF7 and AF8 data.

    Raises:
        SystemExit: If no LSL stream is found or no sample is received.
    """

    def get_inlet():
        streams = resolve_streams(wait_time=2.0)
        eeg_stream = None
        for stream in streams:
            if stream.name() == "PetalStream_eeg":
                eeg_stream = stream
                break
        if eeg_stream is None:
            logging.error("No LSL stream named 'PetalStream_eeg' found.")
            exit(1)
        return StreamInlet(eeg_stream)

    inlet = get_inlet()
    buffer = []
    while True:
        sample, timestamp = inlet.pull_sample(timeout=1)
        if sample is None:
            logging.error("No sample received from LSL stream.")
            exit(1)

        # sample[1, 2, 3, 4, 5] = [TP9, AF7, AF8, TP10, AUX]
        af7 = sample[1]
        af8 = sample[2]
        buffer.append([af7, af8])

        if len(buffer) >= RMS_WINDOW_SIZE:
            yield np.array(buffer)  # Yield to main.py here
            buffer.clear()


# Filter design
nyquist_freq = FS / 2

# Butterworth bandpass filter design
low = BANDPASS_LOW_CUT / nyquist_freq
high = BANDPASS_HIGH_CUT / nyquist_freq
bandpass_b, bandpass_a = butter(BANDPASS_ORDER, [low, high], btype="band")

# Notch filter design
w0 = NOTCH_TARGET_FREQ / nyquist_freq  # w(=omega) = (2pi*f)/fs
notch_b, notch_a = iirnotch(w0, NOTCH_QUALITY_FACTOR)


def process_buffer(buffer):
    """
    Processes a buffer of EOG data by applying spatial filtering, bandpass filtering,
    notch filtering, and then calculates the Root Mean Square (RMS).

    This function takes raw EOG data from AF7 and AF8 channels, applies spatial
    filtering by averaging the channels, then filters the data using a bandpass
    filter (0.5-50 Hz) and a notch filter (to remove noise), and finally computes
    the RMS value for blink detection.

    Args:
        buffer (np.ndarray): A 2D array of shape (RMS_WINDOW_SIZE, 2) containing
            raw EOG data from AF7 (column 0) and AF8 (column 1).

    Returns:
        float: The RMS value of the filtered combined data.
    """

    # Average the two channels first (spatial filtering) to improve SNR
    raw_data_combined = (buffer[:, 0] + buffer[:, 1]) / 2

    # Apply bandpass and notch filters
    filtered_data = filtfilt(
        notch_b, notch_a, filtfilt(bandpass_b, bandpass_a, raw_data_combined)
    )

    # Calculate RMS
    rms = np.sqrt(np.mean(np.square(filtered_data)))

    return rms
