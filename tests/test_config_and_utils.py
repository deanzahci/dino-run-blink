import sys
import unittest
from pathlib import Path

import numpy as np
from unittest import mock

# Ensure the src directory is on the import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import config  # noqa: E402  pylint: disable=wrong-import-position
import utils  # noqa: E402  pylint: disable=wrong-import-position


class ConfigVerificationTests(unittest.TestCase):
    def test_verify_config_parameters_passes_with_defaults(self):
        """Default configuration should satisfy all assertions."""
        # Should not raise
        config.verify_config_parameters()

    def test_verify_config_parameters_raises_when_window_too_large(self):
        """Sliding window larger than available RMS windows should fail."""
        rms_windows = int(
            np.ceil((config.MAX_DISPLAY_TIME * config.FS) / config.RMS_BUFFER_SIZE)
        )
        with mock.patch.object(config, "SLIDING_WINDOW_SIZE", rms_windows + 1):
            with self.assertRaises(AssertionError):
                config.verify_config_parameters()

    def test_verify_config_parameters_raises_when_threshold_too_high(self):
        """Sliding window threshold must not exceed window size."""
        with mock.patch.object(
            config, "SLIDING_WINDOW_THRESHOLD", config.SLIDING_WINDOW_SIZE + 1
        ):
            with self.assertRaises(AssertionError):
                config.verify_config_parameters()


class ProcessBufferTests(unittest.TestCase):
    def test_process_buffer_matches_manual_pipeline(self):
        """process_buffer() should match the manual filtering + RMS pipeline."""
        rng = np.random.default_rng(seed=42)
        buffer = rng.normal(size=(config.RMS_BUFFER_SIZE, 2))

        result = utils.process_buffer(buffer)

        combined = (buffer[:, 0] + buffer[:, 1]) / 2
        if utils.is_bandpass_order_greater_than_2:
            bandpassed = utils.sosfiltfilt(utils.bandpass_sos, combined)
        else:
            bandpassed = utils.filtfilt(utils.bandpass_b, utils.bandpass_a, combined)
        notched = utils.filtfilt(utils.notch_b, utils.notch_a, bandpassed)
        expected = float(np.sqrt(np.mean(np.square(notched))))

        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, expected, places=10)


if __name__ == "__main__":
    unittest.main()
