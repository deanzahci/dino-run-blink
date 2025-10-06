import numpy as np
from pylsl import StreamInlet, resolve_streams
from scipy.signal import butter, filtfilt
import logging

from config import RMS_WINDOW_SIZE, FS


def get_inlet():
    streams = resolve_streams(wait_time=2.0)
    eeg_stream = None

    for stream in streams:
        if stream.name() == "PetalStream_eeg":
            eeg_stream = stream
            break

    if eeg_stream is None:
        print("Stream not found")
        exit(1)

    print("Inlet Created")
    return StreamInlet(eeg_stream)

def stream():
    inlet = get_inlet() # Only called once when the generator is first invoked
    buffer = []
    while True:
        sample, timestamp = inlet.pull_sample(timeout=1)
        if sample is None:
            logging.warning("No sample received from LSL stream.")
            exit(1)

        # sample[1, 2, 3, 4, 5] = [TP9, AF7, AF8, TP10, AUX]
        af7 = sample[1]
        af8 = sample[2]
        buffer.append([af7, af8])

        if len(buffer) >= RMS_WINDOW_SIZE:
            yield np.array(buffer) # Yield to main.py here
            buffer = []

def process_data(buffer):
    af7_data = np.array(buffer[:, 0], dtype=np.float64)
    af8_data = np.array(buffer[:, 1], dtype=np.float64)

    def butter_bandpass(lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype="band")
        return b, a

    def apply_bandpass_filter(data, fs, lowcut=0.5, highcut=50.0, order=2):
        b, a = butter_bandpass(lowcut, highcut, fs, order)
        return filtfilt(b, a, data)

    # Bandpass filter
    af7_data = apply_bandpass_filter(af7_data, FS)
    af8_data = apply_bandpass_filter(af8_data, FS)

    # Individual RMS
    rms_af7 = np.sqrt(np.mean(np.square(af7_data)))
    rms_af8 = np.sqrt(np.mean(np.square(af8_data)))

    # Combined RMS (The average of RMS_AF7 and RMS_AF8)
    combined_rms = (rms_af7 + rms_af8) / 2

    return rms_af7, rms_af8, combined_rms
