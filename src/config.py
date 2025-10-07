# Basic
BLINK_THRESHOLD_INIT = 400  # Initial RMS threshold for blink detection
FS = 256  # Sampling frequency of Muse 2
KEYBOARD_ACTION = " "  # Space for jump

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