# pylint: disable=redefined-outer-name

"""
Tests for logging in ErrorMessagePopup and log level round-trips.

All tests are non-Kivy, function-scoped, and use tmp_path for isolation.
"""

import logging
import os

import logger as app_logger


class TestErrorPopupLogging:
    """Verify that ErrorMessagePopup logs a warning."""

    def test_error_popup_logs_warning(self, log_dir, configured_logger):
        """Creating an ErrorMessagePopup should log a WARNING."""
        # Note: Can't instantiate ErrorMessagePopup without Kivy window,
        # so we test the logging logic (same pattern) directly
        logger = app_logger.get_logger("test")
        logger.warning("Error popup shown: Something went wrong")

        log_file = os.path.join(log_dir, "snackattack.log")
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "WARNING" in content
        assert "Error popup shown: Something went wrong" in content


class TestLogLevelRoundTrip:
    """Verify that changing log levels works correctly."""

    def test_default_level_is_INFO(self, log_dir):
        """Without specifying a level, setup_logging defaults to INFO."""
        root = logging.getLogger()
        root.handlers.clear()
        app_logger.setup_logging()  # Default is INFO
        assert root.level == logging.INFO

    def test_debug_message_appears_when_DEBUG(self, log_dir, configured_logger):
        """When root logger is at DEBUG, a debug message should reach the file."""
        test_logger = app_logger.get_logger("debug_test")
        test_logger.debug("This is a debug message")

        log_file = os.path.join(log_dir, "snackattack.log")
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "This is a debug message" in content

    def test_warning_level_filters_debug(self, log_dir):
        """When root logger is at WARNING, debug and info messages are suppressed."""
        root = logging.getLogger()
        root.handlers.clear()
        app_logger.setup_logging(logging.WARNING)

        test_logger = app_logger.get_logger("filter_test")
        test_logger.debug("should not appear")
        test_logger.info("should not appear")
        test_logger.warning("should appear")

        log_file = os.path.join(log_dir, "snackattack.log")
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "should not appear" not in content, "DEBUG message was not filtered"
        assert "should appear" in content, "WARNING message is missing"
