from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from pylsl import StreamInlet, resolve_streams
from pynput.keyboard import Controller
from scipy.signal import butter, filtfilt

# Config
BLINK_THRESHOLD = 800
MAX_TIME = 5  # seconds
Y_MIN = 0
Y_MAX = 2000
ACTION = " "

# Constants
BUFFER_SIZE = 20
FS = 256


def get_inlet():
    print("Resolving streams")
    streams = resolve_streams(wait_time=2.0)
    eeg_stream = None
    for stream in streams:
        if stream.name() == "PetalStream_eeg":
            eeg_stream = stream
            break
    if eeg_stream is None:
        print("Stream not found")
        exit(1)
    print("Inlet created")
    return StreamInlet(eeg_stream)


def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def apply_bandpass_filter(data, fs, lowcut=0.5, highcut=50.0, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data)


keyboard = Controller()


def process_data(buffer):
    af7_data = np.array(buffer[:, 0], dtype=np.float64)  # AF7 (Index 1)
    af8_data = np.array(buffer[:, 1], dtype=np.float64)  # AF8 (Index 2)

    # Bandpass filter
    af7_data = apply_bandpass_filter(af7_data, FS)
    af8_data = apply_bandpass_filter(af8_data, FS)

    # Individual RMS
    rms_af7 = np.sqrt(np.mean(np.square(af7_data)))
    rms_af8 = np.sqrt(np.mean(np.square(af8_data)))

    # Combined RMS (The average of RMS_AF7 and RMS_AF8)
    combined_rms = np.sqrt((rms_af7**2 + rms_af8**2) / 2)

    return rms_af7, rms_af8, combined_rms


def detect_blink(combined_rms, threshold):
    return combined_rms > threshold


def trigger_action():
    if action:
        keyboard.press(ACTION)
        keyboard.release(ACTION)


def stream():
    inlet = get_inlet()
    buffer = []
    while True:
        sample, timestamp = inlet.pull_sample(timeout=1)
        if sample is not None and len(sample) >= 3:
            af7 = sample[1]
            af8 = sample[2]
            buffer.append([af7, af8])

            if len(buffer) >= BUFFER_SIZE:
                yield np.array(buffer)
                buffer = []


def main():
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    max_time = MAX_TIME
    max_samples = max_time * FS

    all_rms_af7 = deque(maxlen=max_samples)
    all_rms_af8 = deque(maxlen=max_samples)
    all_combined_rms = deque(maxlen=max_samples)
    all_time = deque(maxlen=max_samples)
    blink_times = deque(maxlen=10)

    max_value = 0

    current_time = 0.0
    dt = 1.0 / FS

    for buffer in stream():
        rms_af7, rms_af8, combined_rms = process_data(buffer)
        if combined_rms < Y_MAX and combined_rms > max_value:
            max_value = combined_rms
            print("New max combined RMS:", max_value)

        block_length = BUFFER_SIZE
        time_block = np.linspace(
            current_time, current_time + block_length * dt, block_length, endpoint=False
        )
        current_time += block_length * dt

        all_time.extend(time_block)
        all_rms_af7.extend([rms_af7] * block_length)
        all_rms_af8.extend([rms_af8] * block_length)
        all_combined_rms.extend([combined_rms] * block_length)

        if detect_blink(combined_rms, BLINK_THRESHOLD):
            trigger_action()
            blink_times.append(time_block[block_length // 2])

        ax.clear()

        # AF7 and AF8 RMS
        ax.plot(
            all_time,
            all_rms_af7,
            label="RMS AF7",
            color="black",
            linewidth=1,
            alpha=0.3,
        )
        ax.plot(
            all_time,
            all_rms_af8,
            label="RMS AF8",
            color="black",
            linewidth=1,
            alpha=0.3,
        )

        # Combined RMS
        ax.plot(
            all_time, all_combined_rms, label="Combined RMS", color="blue", linewidth=2
        )

        # Blink detection line
        first_label = True
        for t in blink_times:
            if first_label:
                ax.axvline(
                    x=t,
                    color="red",
                    linestyle="--",
                    linewidth=2,
                    label="Blink Detected",
                )
                first_label = False
            else:
                ax.axvline(x=t, color="red", linestyle="--", linewidth=2)

        # Max RMS
        ax.text(
            0.05,
            0.95,
            f"Max RMS: {max_value:.2f}",
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.5),
        )

        # ax.set_ylim(Y_MIN, Y_MAX)
        ax.set_xlim(max(0, current_time - max_time), current_time)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("RMS Value")
        ax.set_title("EEG Blink Detection (Real-time)")
        ax.legend(loc="upper right")
        plt.pause(0.001)


if __name__ == "__main__":
    action = input("1: Action 2: No Action\n")
    if action == "1":
        action = True
    else:
        action = False

    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting")
        plt.close()
        exit(0)
