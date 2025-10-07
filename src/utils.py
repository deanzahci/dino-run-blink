"""
Utility functions for Dino Run Blink project.

This module provides functions for streaming EEG data from LSL, processing
buffers with filtering and RMS calculation, and designing filters.
"""

import logging

import numpy as np
from pylsl import StreamInlet, resolve_streams
from scipy.signal import butter, iirnotch, sosfiltfilt, filtfilt

from config import (
    FS,
    NYQUIST_FREQ,
    BANDPASS_HIGH_CUT,
    BANDPASS_LOW_CUT,
    BANDPASS_ORDER,
    RMS_BUFFER_SIZE,
    NOTCH_TARGET_FREQ,
    NOTCH_QUALITY_FACTOR,
)


def stream():
    """
    Generator function that streams EOG data from LSL and yields buffers.

    This function connects to the LSL stream named "PetalStream_eeg", collects
    samples from AF7 and AF8 channels into a buffer, and yields the buffer when
    it reaches the specified RMS_WINDOW_SIZE. It includes error handling for
    missing or incomplete samples, exiting after a threshold of failures.

    Yields:
        np.ndarray: A 2D array of shape (RMS_WINDOW_SIZE, 2) containing AF7 and AF8 data.

    Raises:
        SystemExit: If no LSL stream is found, or if no/incomplete samples are
            received more than 5 times consecutively.
    """

    def _get_inlet():
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

    inlet = _get_inlet()
    buffer = []
    sample_none_count = 0
    sample_none_count_limit = 5
    AF7_CHANNEL_INDEX = 1
    AF8_CHANNEL_INDEX = 2
    while True:
        sample, timestamp = inlet.pull_sample(timeout=1)
        if sample is None or len(sample) < AF8_CHANNEL_INDEX + 1:
            sample_none_count += 1
            if sample_none_count >= sample_none_count_limit:
                logging.error(
                    f"No samples or incomplete samples received more than {sample_none_count_limit} times. Exiting."
                )
                exit(1)
            else:
                logging.warning(
                    "No sample received from LSL stream or sample is incomplete."
                )
                continue
        sample_none_count = 0

        # sample[1, 2, 3, 4, 5] = [TP9, AF7, AF8, TP10, AUX]
        af7 = sample[AF7_CHANNEL_INDEX]
        af8 = sample[AF8_CHANNEL_INDEX]
        buffer.append([af7, af8])

        if len(buffer) >= RMS_BUFFER_SIZE:
            yield np.array(buffer)  # Yield to main.py here
            buffer.clear()


# Butterworth bandpass filter design
low = BANDPASS_LOW_CUT / NYQUIST_FREQ
high = BANDPASS_HIGH_CUT / NYQUIST_FREQ
if BANDPASS_ORDER > 2:
    is_bandpass_order_greater_than_2 = True
    # Use second-order sections (SOS) for numerical stability with higher-order filters
    bandpass_sos = butter(BANDPASS_ORDER, [low, high], btype="band", output="sos")
else:
    is_bandpass_order_greater_than_2 = False
    bandpass_b, bandpass_a = butter(BANDPASS_ORDER, [low, high], btype="band")

# Notch filter design
notch_b, notch_a = iirnotch(NOTCH_TARGET_FREQ, NOTCH_QUALITY_FACTOR, fs=FS)


def process_buffer(buffer):
    """
    Processes a buffer of EOG data by applying spatial filtering, bandpass filtering,
    notch filtering, and then calculates the Root Mean Square (RMS).

    This function takes raw EOG data from AF7 and AF8 channels, applies spatial
    filtering by averaging the channels, then filters the data using a bandpass
    filter (0.5-50 Hz) and a notch filter (to remove noise). For bandpass filters
    with order > 2, it uses second-order sections (SOS) for stability. Finally,
    it computes the RMS value for blink detection.

    Args:
        buffer (np.ndarray): A 2D array of shape (RMS_WINDOW_SIZE, 2) containing
            raw EOG data from AF7 (column 0) and AF8 (column 1).

    Returns:
        float: The RMS value of the filtered combined data.

    Raises:
        AssertionError: If the buffer size does not match RMS_WINDOW_SIZE.
    """

    assert (
        buffer.shape[0] == RMS_BUFFER_SIZE
    ), f"Buffer size {buffer.shape[0]} does not match RMS_WINDOW_SIZE {RMS_BUFFER_SIZE}"

    # Average the two channels first (spatial filtering) to improve SNR
    raw_data_combined = (buffer[:, 0] + buffer[:, 1]) / 2

    # Apply bandpass filter first to remove broad noise, then notch filter for specific frequencies
    if is_bandpass_order_greater_than_2:
        bandpass_filtered_data = sosfiltfilt(bandpass_sos, raw_data_combined)
    else:
        bandpass_filtered_data = filtfilt(bandpass_b, bandpass_a, raw_data_combined)
    notch_filtered_data = filtfilt(notch_b, notch_a, bandpass_filtered_data)
    filtered_data = notch_filtered_data

    # Calculate RMS to quantify signal energy for blink detection
    rms = np.sqrt(np.mean(np.square(filtered_data)))

    return rms
