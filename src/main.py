from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from pynput.keyboard import Controller

from config import (ACTION, BLINK_THRESHOLD, FS, MAX_DISPLAY_TIME,
                    RMS_WINDOW_SIZE, Y_MAX)
from plot import plot_data
from utils import process_data, stream

is_calibration_done = False
keyboard = Controller()


def main():
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.show(block=False)

    # Deques for storing time and RMS values
    MAX_SAMPLE_NUM = MAX_DISPLAY_TIME * FS + 10  # Extra 10 for buffer
    deque_time = deque(maxlen=MAX_SAMPLE_NUM)
    deque_rms_af7 = deque(maxlen=MAX_SAMPLE_NUM)
    deque_rms_af8 = deque(maxlen=MAX_SAMPLE_NUM)
    deque_rms_combined = deque(maxlen=MAX_SAMPLE_NUM)
    deque_blink_times = deque(maxlen=100)

    max_value = 0
    current_data_index = 0.0
    y_max = Y_MAX  # Updated dynamically
    rms_window_size = RMS_WINDOW_SIZE
    DELTA_T = 1 / FS  # Time interval between samples (when FS = 256, DELTA_T = ~0.0039s)

    # Main loop to process incoming data and update plot
    for buffer in stream():  # Stream is a generator function
        rms_af7, rms_af8, combined_rms = process_data(buffer)
        if combined_rms > max_value:
            max_value = combined_rms
            if max_value >= y_max:
                y_max = (max_value // 100) * 100 + 100  # Increase by 100 steps

        # Divide the time into segments for the RMS window
        rms_window = np.linspace(
            current_data_index,
            current_data_index + (rms_window_size * DELTA_T),
            rms_window_size,
            endpoint=False,
        )
        current_data_index += rms_window_size * DELTA_T

        # Extend the deques with the new data
        deque_time.extend(rms_window)
        deque_rms_af7.extend(np.full(rms_window_size, rms_af7))
        deque_rms_af8.extend(np.full(rms_window_size, rms_af8))
        deque_rms_combined.extend(np.full(rms_window_size, combined_rms))

        # Detect blink and perform action if enabled
        if combined_rms > BLINK_THRESHOLD:
            deque_blink_times.append(rms_window[rms_window_size // 2])
            if is_action_enabled and (
                is_calibration_done or not is_calibration_enabled
            ):
                keyboard.press(is_action_enabled)
                keyboard.release(is_action_enabled)

        plot_data(
            fig,
            ax,
            deque_time,
            deque_rms_af7,
            deque_rms_af8,
            deque_rms_combined,
            deque_blink_times,
            max_value,
            current_data_index,
            y_max,
        )


if __name__ == "__main__":
    print("Welcome to Dino Run Blink")
    if input("0: No Calibrate 1: Calibrate\n") == "1":
        is_calibration_enabled = True
    else:
        is_calibration_enabled = False
    if input("0: No Action 1: Action\n") == "1":
        is_action_enabled = ACTION
    else:
        is_action_enabled = None

    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        plt.close()
        exit(0)
