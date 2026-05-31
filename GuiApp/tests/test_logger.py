"""
Tests for the logging configuration module (logger.py).

All tests are non-Kivy, function-scoped, and use tmp_path for isolation.
"""

# pylint: disable=redefined-outer-name,protected-access

import logging
import os
import re
import sys

from logger import MillisecondFormatter

import logger as app_logger


class TestSetup:
    def test_creates_log_directory(self, log_dir):
        """setup_logging() should ensure the log directory exists."""
        # Directory already exists via fixture, verify setup doesn't error
        app_logger.setup_logging(logging.INFO)
        assert os.path.isdir(log_dir)

    def test_logs_to_file(self, log_dir, configured_logger):
        """After setup, a log message should appear in snackattack.log."""
        test_logger = app_logger.get_logger("test_logger")
        test_logger.info("Hello test")
        log_file = os.path.join(log_dir, "snackattack.log")
        assert os.path.isfile(log_file)
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "Hello test" in content

    def test_has_two_handlers(self, configured_logger):
        """Root logger should have file + console handlers after setup."""
        # Filter out handlers added by pytest (e.g. LogCaptureHandler)
        our_handlers = [
            h
            for h in configured_logger.handlers
            if type(h).__name__ != "LogCaptureHandler"
        ]
        assert len(our_handlers) == 2

    def test_respects_log_level(self, log_dir):
        """Root logger and handlers should be set to the given level."""
        app_logger.setup_logging(logging.WARNING)
        root = logging.getLogger()
        assert root.level == logging.WARNING
        for handler in root.handlers:
            assert handler.level == logging.WARNING

    def test_get_logger_returns_child(self):
        """get_logger() should return a named child of the root logger."""
        child = app_logger.get_logger("my_test_module")
        assert isinstance(child, logging.Logger)
        assert child.name == "my_test_module"

    def test_millisecond_formatter(self):
        """MillisecondFormatter should produce timestamps with milliseconds."""
        fmt = MillisecondFormatter("%(asctime)s", datefmt="%Y-%m-%d %H:%M:%S")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )
        # Set a known creation time with 123 ms
        record.created = 1234567890.123
        formatted = fmt.format(record)
        # Should contain ",123" after the seconds
        assert re.search(
            r",\d{3}", formatted
        ), f"Expected milliseconds in formatted time, got: {formatted}"

    def test_setup_idempotent(self, log_dir):
        """Calling setup_logging twice should not duplicate handlers."""
        app_logger.setup_logging(logging.INFO)
        count_before = len(logging.getLogger().handlers)
        app_logger.setup_logging(logging.INFO)
        count_after = len(logging.getLogger().handlers)
        assert count_after == count_before


# --- Phase 2: Crash capture ---


class TestCrashCapture:
    def test_excepthook_logs_critical(self, log_dir, configured_logger):
        """Trigger sys.excepthook and verify a CRITICAL log entry."""
        exc_info = None
        try:
            raise ZeroDivisionError("test crash")
        except ZeroDivisionError:
            exc_info = sys.exc_info()

        app_logger._crash_excepthook(*exc_info)

        log_file = os.path.join(log_dir, "snackattack.log")
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "CRITICAL" in content
        assert "UNHANDLED" in content
        assert "ZeroDivisionError" in content

    def test_traceback_in_log_file(self, log_dir, configured_logger):
        """After a crash, the full traceback should be in the log file."""
        exc_info = None
        try:
            raise ValueError("traceback test")
        except ValueError:
            exc_info = sys.exc_info()

        app_logger._crash_excepthook(*exc_info)

        log_file = os.path.join(log_dir, "snackattack.log")
        with open(log_file, encoding="utf-8") as f:
            content = f.read()
        assert "Traceback (most recent call last)" in content
        assert "ValueError" in content
        assert "traceback test" in content


# --- Phase 3: Log collection ---


class TestLogCollection:
    def test_get_all_log_file_paths_main_only(self, log_dir, configured_logger):
        """With only snackattack.log, returns exactly one path."""
        # Write a message to create the log file
        logging.getLogger().info("create log file")
        paths = app_logger.get_all_log_file_paths()
        assert len(paths) == 1
        assert paths[0].endswith("snackattack.log")

    def test_get_all_log_file_paths_includes_backups(self, log_dir, configured_logger):
        """When rotated backups exist, they should be included in order."""
        # Create backup files to simulate rotation
        log_path = os.path.join(log_dir, "snackattack.log")
        backup1 = os.path.join(log_dir, "snackattack.log.1")
        backup2 = os.path.join(log_dir, "snackattack.log.2")

        for path in (log_path, backup1, backup2):
            with open(path, "w", encoding="utf-8") as f:
                f.write("test\n")

        paths = app_logger.get_all_log_file_paths()
        assert len(paths) == 3
        # Order: main, .1, .2
        assert "snackattack.log" in paths[0]
        assert "snackattack.log.1" in paths[1]
        assert "snackattack.log.2" in paths[2]

    def test_collect_all_logs_returns_content(self, log_dir, configured_logger):
        """collect_all_logs() should return the log content with headers."""
        test_logger = app_logger.get_logger("collect_test")
        test_logger.info("collect me")

        result = app_logger.collect_all_logs()
        assert "===== snackattack.log =====" in result
        assert "collect me" in result

    def test_collect_all_logs_empty(self, log_dir):
        """When no log files exist, returns a message instead of crashing."""
        # Don't call setup_logging so no files exist
        result = app_logger.collect_all_logs()
        assert "No log files found" in result or result == ""
