"""
LogScreen — displays application logs in a scrollable view with USB export.

Uses logger.collect_all_logs() and logger.get_all_log_file_paths() to
retrieve log data. Uses USBManager for USB detection and file copying,
with typed exceptions caught here and shown via ErrorMessagePopup.
"""

import logging
import os
import logger as app_logger
from logger import get_logger
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.removeConfirmationPopup import RemoveConfirmationPopup


logger = get_logger(__name__)


class LogScreen(GridLayoutScreen):
    """Screen that displays application and crash logs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)
        self.ids.clearLogsButton.bind(on_release=self.clear_logs)

    def on_back_button_pressed(self, *args):
        """Navigate back to admin screen."""
        self.manager.transitionToScreen("adminScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        """Populate log content when the screen is shown."""
        self.refresh_logs()

    def refresh_logs(self, *_args):
        """Re-read all log files and populate the RecycleView, scrolling to bottom."""
        log_text = app_logger.collect_all_logs()
        # Split into individual lines for RecycleView virtual scrolling
        log_lines = log_text.splitlines()
        # Keep only last 5000 lines (RecycleView handles this efficiently)
        MAX_LOG_LINES = 5000
        if len(log_lines) > MAX_LOG_LINES:
            log_lines = log_lines[-MAX_LOG_LINES:]
        self.ids.logRecycleView.data = [{"log_text": line} for line in log_lines]
        # Scroll to bottom (0 = bottom for RecycleView)
        self.ids.logRecycleView.scroll_y = 0
        logger.debug("Log screen refreshed (%d lines)", len(log_lines))

    def clear_logs(self, *_args):
        """Show confirmation popup, then clear all log files."""

        def on_confirmed(*_args):
            # Flush all logging handlers to avoid partial writes
            for handler in logging.getLogger().handlers:
                handler.flush()

            log_dir = app_logger.LOG_DIR
            cleared_count = 0
            for entry in os.listdir(log_dir):
                if entry.startswith("snackattack.log"):
                    file_path = os.path.join(log_dir, entry)
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.truncate(0)
                        cleared_count += 1
                    except OSError as e:
                        logger.error("Failed to clear %s: %s", entry, e)

            logger.info("Cleared %d log files", cleared_count)
            self.refresh_logs()

        popup = RemoveConfirmationPopup(
            question_text="Are you sure you want to clear all logs?\nThis action cannot be undone.",
            custom_remove_button_text="Clear",
        )
        popup.bind(on_removed=on_confirmed)
        popup.open()
