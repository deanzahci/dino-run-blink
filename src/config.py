# Basic
BLINK_THRESHOLD_INIT = 400  # Initial RMS threshold for blink detection
KEYBOARD_ACTION = " "  # Space for jump

# Fixed for Muse 2
FS = 256  # Sampling frequency of Muse 2
NYQUIST_FREQ = FS / 2  # Nyquist frequency

# Visualization
MAX_DISPLAY_TIME = 5  # Seconds
Y_MAX_INIT = 1000  # Initial y-axis max value

# RMS sliding window voting classifier
RMS_WINDOW_SIZE = 16  # Number of samples to calculate RMS
SLIDING_WINDOW_SIZE = 10
SLIDING_WINDOW_THRESHOLD = 2

# Bandpass filter
BANDPASS_HIGH_CUT = 10.0  # High cut frequency for bandpass filter
BANDPASS_LOW_CUT = 0.5  # Low cut frequency for bandpass filter
BANDPASS_ORDER = 2  # Order of the bandpass filter

# Notch filter
NOTCH_TARGET_FREQ = 60.0  # Target frequency to be removed from signal (Hz)
NOTCH_QUALITY_FACTOR = 30.0  # Quality factor for notch filter


def verify_config_parameters():
    """
    Verify that the configuration parameters are valid.
    """
    assert BLINK_THRESHOLD_INIT > 0, "BLINK_THRESHOLD_INIT must be positive"
    assert FS > 0, "FS must be positive"
    assert NYQUIST_FREQ == FS / 2, "Nyquist frequency must be FS / 2"
    assert KEYBOARD_ACTION != "", "KEYBOARD_ACTION must be a non-empty string"
    assert MAX_DISPLAY_TIME > 0, "MAX_DISPLAY_TIME must be positive"
    assert Y_MAX_INIT > 0, "Y_MAX_INIT must be positive"
    assert RMS_WINDOW_SIZE > 0, "RMS_WINDOW_SIZE must be positive"
    assert SLIDING_WINDOW_SIZE > 0, "SLIDING_WINDOW_SIZE must be positive"
    assert (
        SLIDING_WINDOW_THRESHOLD < SLIDING_WINDOW_SIZE
    ), "SLIDING_WINDOW_THRESHOLD must be less than SLIDING_WINDOW_SIZE"
    assert (
        BANDPASS_LOW_CUT < BANDPASS_HIGH_CUT
    ), "BANDPASS_LOW_CUT must be less than BANDPASS_HIGH_CUT"
    assert (
        BANDPASS_HIGH_CUT < NYQUIST_FREQ
    ), "BANDPASS_HIGH_CUT must be less than Nyquist frequency"
    assert (
        BANDPASS_ORDER >= 2
    ), "BANDPASS_ORDER must be at least 2 since we use sosfiltfilt"
    assert (
        NOTCH_TARGET_FREQ < NYQUIST_FREQ
    ), "NOTCH_TARGET_FREQ must be less than Nyquist frequency"
    assert NOTCH_QUALITY_FACTOR > 0, "NOTCH_QUALITY_FACTOR must be positive"
