import logging
from collections import deque

import numpy as np
from matplotlib import pyplot as plt
from pynput.keyboard import Controller

from config import (
    BLINK_THRESHOLD_INIT,
    FS,
    KEYBOARD_ACTION,
    MAX_DISPLAY_TIME,
    RMS_WINDOW_SIZE,
    SLIDING_WINDOW_SIZE,
    SLIDING_WINDOW_THRESHOLD,
    Y_MAX_INIT,
)
from plot import plot_data
from utils import process_buffer, stream

is_calibration_done = False
keyboard = Controller()


def main():
    # Deques for storing time and RMS values
    MAX_SAMPLE_NUM = MAX_DISPLAY_TIME * FS + 5  # Extra 5 for buffer
    deque_time = deque(maxlen=MAX_SAMPLE_NUM)
    deque_rms_combined = deque(maxlen=MAX_SAMPLE_NUM)
    deque_blink_times = deque(maxlen=100)
    deque_detection_history = deque(maxlen=SLIDING_WINDOW_SIZE)

    # Initialize plot
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.show(block=False)

    max_value = 0
    current_data_index = 0.0
    y_max = Y_MAX_INIT  # Updated dynamically
    rms_window_size = RMS_WINDOW_SIZE
    TIME_DELTA = (
        1 / FS
    )  # Time interval between samples (when FS = 256, DELTA_T = ~0.0039s)

    # Main loop to process incoming data and update plot
    for buffer in stream():  # Stream is a generator function
        rms = process_buffer(buffer)
        if rms > max_value:
            max_value = rms
            if max_value >= y_max:
                y_max = (max_value // 100) * 100 + 100  # Increase by 100 steps

        # Divide the time into segments for the RMS window
        rms_window = np.linspace(
            current_data_index,
            current_data_index + (rms_window_size * TIME_DELTA),
            rms_window_size,
            endpoint=False,
        )
        current_data_index += rms_window_size * TIME_DELTA

        # Extend the deques with the new data
        deque_time.extend(rms_window)
        deque_rms_combined.extend(np.full(rms_window_size, rms))

        # Sliding window voting
        deque_detection_history.append(rms > BLINK_THRESHOLD_INIT)
        if deque_detection_history.count(True) > SLIDING_WINDOW_THRESHOLD:
            # Refractory period to avoid multiple detections
            deque_detection_history.extend(np.full(SLIDING_WINDOW_SIZE, False))
            deque_blink_times.append(rms_window[rms_window_size // 2])
            if is_action_enabled and (
                is_calibration_done or not is_calibration_enabled
            ):
                keyboard.press(is_action_enabled)
                keyboard.release(is_action_enabled)

        plot_data(
            ax=ax,
            fig=fig,
            deque_time=deque_time,
            deque_rms_combined=deque_rms_combined,
            deque_blink_times=deque_blink_times,
            max_value=max_value,
            current_data_index=current_data_index,
            y_max=y_max,
        )


if __name__ == "__main__":
    logging.info("Welcome to Dino Run Blink")
    if input("0: No Calibrate 1: Calibrate\n") == "1":
        is_calibration_enabled = True
    else:
        is_calibration_enabled = False
    if input("0: No Action 1: Action\n") == "1":
        is_action_enabled = KEYBOARD_ACTION
    else:
        is_action_enabled = None

    main()
