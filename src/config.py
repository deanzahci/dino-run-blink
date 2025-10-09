"""Configuration constants for Dino Run Blink.

Keep values small and explicit here. The `verify_config_parameters` function
validates assumptions used throughout the codebase (filter designs, buffer
sizes, thresholds). Only update values if you understand the implications on
filtering and buffering, and do not change the assert conditions unless you truly
understand the ramifications and rationale behind them.
"""

import logging
from math import ceil

# =============================================================================
# BASIC SETTINGS
# =============================================================================

# Blink detection
BLINK_THRESHOLD_INIT = 400  # Initial RMS threshold for blink detection

# Keyboard control
KEYBOARD_ACTION = " "  # Space key for jump action

# =============================================================================
# HARDWARE/SAMPLING SETTINGS (Fixed for Muse 2)
# =============================================================================

FS = 256  # Sampling frequency of Muse 2 (Hz)
NYQUIST_FREQ = FS / 2  # Nyquist frequency (Hz)

# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================

MAX_DISPLAY_TIME = 5  # Display time window (seconds)
Y_MAX_INIT = 1000  # Initial y-axis maximum value

# =============================================================================
# RMS PROCESSING SETTINGS
# =============================================================================

RMS_BUFFER_SIZE = 16  # Number of samples per RMS calculation window

# Sliding window voting for blink detection
SLIDING_WINDOW_SIZE = 5  # Size of sliding window for voting
SLIDING_WINDOW_THRESHOLD = 2  # Minimum votes needed for blink detection

# =============================================================================
# FILTER SETTINGS
# =============================================================================

# Bandpass filter (0.5-10 Hz for blink signals)
BANDPASS_LOW_CUT = 0.5  # Low cutoff frequency (Hz)
BANDPASS_HIGH_CUT = 10.0  # High cutoff frequency (Hz)
BANDPASS_ORDER = 2  # Filter order

# Notch filter (60 Hz power line interference)
NOTCH_TARGET_FREQ = 60.0  # Target frequency to remove (Hz)
NOTCH_QUALITY_FACTOR = 30.0  # Quality factor (Q-factor)

# Padding for filter stability
PADLEN = min(
    RMS_BUFFER_SIZE - 1, 3 * BANDPASS_ORDER
)  # Pad length for filtfilt/sosfiltfilt

# =============================================================================
# CALIBRATION SETTINGS
# =============================================================================

CALIBRATION_RMS_NUM = 320  # Number of RMS values to collect for calibration
CALIBRATION_WAIT_TIME = 5  # Wait time before calibration starts (seconds)
CALIBRATION_AFTER_TIME = 5  # Wait time after calibration before action (seconds)

# MAD (Median Absolute Deviation) calibration parameters
MAD_K = 3  # Threshold multiplier (range: 2-4, higher for noisy signals)
MAD_SCALE_FACTOR = 1.4826  # Scale factor for Gaussian consistency


def verify_config_parameters():
    """Verify that configuration constants satisfy required assumptions.

    This function intentionally raises AssertionError when a configuration
    parameter is invalid. The assertions are relied upon by other modules and
    should be kept as-is unless you understand the ramifications.
    """
    # Basic positive value checks
    assert BLINK_THRESHOLD_INIT > 0, "BLINK_THRESHOLD_INIT must be positive"
    assert FS > 0, "FS must be positive"
    assert MAX_DISPLAY_TIME > 0, "MAX_DISPLAY_TIME must be positive"
    assert Y_MAX_INIT > 0, "Y_MAX_INIT must be positive"
    assert RMS_BUFFER_SIZE > 0, "RMS_BUFFER_SIZE must be positive"
    assert NOTCH_QUALITY_FACTOR > 0, "NOTCH_QUALITY_FACTOR must be positive"
    assert MAD_K > 0, "MAD_K must be positive"
    assert MAD_SCALE_FACTOR > 0, "MAD_SCALE_FACTOR must be positive"
    assert CALIBRATION_RMS_NUM > 0, "CALIBRATION_RMS_NUM must be positive"
    assert CALIBRATION_WAIT_TIME >= 0, "CALIBRATION_WAIT_TIME must be non-negative"
    assert CALIBRATION_AFTER_TIME >= 0, "CALIBRATION_AFTER_TIME must be non-negative"

    # Hardware constraints
    assert NYQUIST_FREQ == FS / 2, "Nyquist frequency must be FS / 2"
    assert KEYBOARD_ACTION != "", "KEYBOARD_ACTION must be a non-empty string"

    # Frequency range checks
    assert (
        0 < BANDPASS_LOW_CUT < NYQUIST_FREQ
    ), "BANDPASS_LOW_CUT must be between 0 and Nyquist frequency"
    assert (
        0 < BANDPASS_HIGH_CUT < NYQUIST_FREQ
    ), "BANDPASS_HIGH_CUT must be between 0 and Nyquist frequency"
    assert (
        0 < NOTCH_TARGET_FREQ < NYQUIST_FREQ
    ), "NOTCH_TARGET_FREQ must be between 0 and Nyquist frequency"

    # RMS processing checks
    rms_windows_in_display = ceil((MAX_DISPLAY_TIME * FS) / RMS_BUFFER_SIZE)
    assert rms_windows_in_display > 0, "RMS settings must yield at least one window"
    assert SLIDING_WINDOW_SIZE <= rms_windows_in_display, (
        f"SLIDING_WINDOW_SIZE ({SLIDING_WINDOW_SIZE}) must be <= number of RMS "
        f"windows in display ({rms_windows_in_display})"
    )
    assert (
        SLIDING_WINDOW_THRESHOLD <= SLIDING_WINDOW_SIZE
    ), "SLIDING_WINDOW_THRESHOLD must be <= SLIDING_WINDOW_SIZE"

    # Filter parameter checks
    assert (
        BANDPASS_LOW_CUT < BANDPASS_HIGH_CUT
    ), "BANDPASS_LOW_CUT must be < BANDPASS_HIGH_CUT"
    assert BANDPASS_ORDER >= 2, "BANDPASS_ORDER must be >= 2 for sosfiltfilt stability"
    assert 0 < PADLEN < RMS_BUFFER_SIZE, "PADLEN must be positive and < RMS_BUFFER_SIZE"

    logging.info("All configuration parameters are valid.")
