import logging
from collections import deque

import numpy as np
from matplotlib import pyplot as plt
from pynput.keyboard import Controller
from scipy.signal import find_peaks

from config import (BLINK_THRESHOLD_INIT, CALIBRATION_AFTER_TIME,
                    CALIBRATION_RMS_NUM, CALIBRATION_WAIT_TIME, FS,
                    KEYBOARD_ACTION, MAX_DISPLAY_TIME, RMS_BUFFER_SIZE,
                    SLIDING_WINDOW_SIZE, SLIDING_WINDOW_THRESHOLD, Y_MAX_INIT,
                    verify_config_parameters)
from plot import plot_data
from utils import get_mad_threshould, process_buffer, stream

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

keyboard = Controller()


def main():
    blink_threshould = BLINK_THRESHOLD_INIT
    is_calibration_done = False

    # Deques for storing time and RMS values
    MAX_SAMPLE_NUM = MAX_DISPLAY_TIME * FS + 5  # Extra 5 for buffer

    # TODO: optmize whether to use deque
    deque_time = deque(maxlen=MAX_SAMPLE_NUM)
    deque_rms_combined = deque(maxlen=MAX_SAMPLE_NUM)
    deque_blink_times = deque(maxlen=100)
    deque_detection_history = deque(maxlen=SLIDING_WINDOW_SIZE)
    calibration_rms_values = []

    # Initialize plot
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.show(block=False)

    max_value = 0
    elapsed_seconds = 0.0
    y_max = Y_MAX_INIT  # Updated dynamically
    rms_window_size = RMS_BUFFER_SIZE
    TIME_DELTA = 1 / FS  # Time interval between samples
    is_calibration_rms_collected = False

    # Main loop to process incoming data and update plot
    for buffer in stream():  # Stream is a generator function
        rms = process_buffer(buffer)
        if rms > max_value:
            max_value = rms
            if max_value >= y_max:
                y_max = (max_value // 100) * 100 + 100  # Increase by 100 steps

        # Divide the time into segments for the RMS window
        rms_window = np.linspace(
            elapsed_seconds,
            elapsed_seconds + (rms_window_size * TIME_DELTA),
            rms_window_size,
            endpoint=False,
        )
        elapsed_seconds += rms_window_size * TIME_DELTA

        # Extend the deques with the new data
        deque_time.extend(rms_window)
        deque_rms_combined.extend(np.full(rms_window_size, rms))

        # TODO: optimize sliding window voting algorithm somehow
        # Sliding window voting algorithm
        if is_calibration_done or not is_calibration_enabled:
            deque_detection_history.append(rms > blink_threshould)
            if deque_detection_history.count(True) > SLIDING_WINDOW_THRESHOLD:
                # Refractory period to avoid multiple detections
                deque_detection_history.extend(np.full(SLIDING_WINDOW_SIZE, False))
                deque_blink_times.append(rms_window[rms_window_size // 2])
                if is_action_enabled and (
                    is_calibration_done or not is_calibration_enabled
                ):
                    # Perform the keyboard action
                    keyboard.press(is_action_enabled)
                    keyboard.release(is_action_enabled)

        plot_data(
            ax=ax,
            fig=fig,
            deque_time=deque_time,
            deque_rms_combined=deque_rms_combined,
            deque_blink_times=deque_blink_times,
            max_value=max_value,
            current_data_index=elapsed_seconds,
            y_max=y_max,
        )

        if is_calibration_done or not is_calibration_enabled:
            continue
        elif elapsed_seconds <= CALIBRATION_WAIT_TIME:
            logging.info(
                "Calibration starts soon: please relax and do not blink for 20 seconds."
            )
        elif (
            len(calibration_rms_values) < CALIBRATION_RMS_NUM
            and not is_calibration_rms_collected
        ):
            calibration_rms_values.append(rms)
            if len(calibration_rms_values) == CALIBRATION_RMS_NUM:
                blink_threshould = get_mad_threshould(calibration_rms_values)
                is_calibration_rms_collected = True
                when_calibration_rms_collected = elapsed_seconds
                logging.info(f"Calibration is done. New blink threshold: {blink_threshould:.2f}")
        elif is_calibration_rms_collected and (
            elapsed_seconds < when_calibration_rms_collected + CALIBRATION_AFTER_TIME
        ):
            if is_action_enabled:
                logging.info(
                    "Calibration is done. The action logic is going to be functional soon."
                )
            else:
                logging.info("Calibration is done, but action is disabled.")
        else:
            is_calibration_done = True  # This will make the action logic functional


if __name__ == "__main__":
    verify_config_parameters()
    print("Welcome to Dino Run Blink")
    if input("0: No Calibrate 1: Calibrate\n") == "1":
        is_calibration_enabled = True
    else:
        is_calibration_enabled = False
    if input("0: No Action 1: Action\n") == "1":
        is_action_enabled = KEYBOARD_ACTION
    else:
        is_action_enabled = None
    main()