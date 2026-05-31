"""
Centralized logging configuration for Snack Attack Track.

Provides:
- setup_logging(): Initialize the root logger with file + console handlers.
                 Installs sys.excepthook and sys.unraisablehook so that
                 unhandled crashes are logged to the main log with full
                 tracebacks (not to separate files).
- get_logger(name): Convenience wrapper around logging.getLogger().
- collect_all_logs(): Read all logs into a display string.
- get_all_log_file_paths(): Get paths of all log files.
"""

import logging
import logging.handlers
import os
import sys
import time
from typing import List


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "snackattack.log")

# Default format strings
LOG_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"  # e.g. 2026-05-28 14:30:45


class MillisecondFormatter(logging.Formatter):
    """Formatter that appends milliseconds to the timestamp."""

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
            s = f"{s},{int(record.msecs):03d}"
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = f"{t},{record.msecs:03d}"
        return s


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name."""
    return logging.getLogger(name)


def _ensure_log_dir() -> None:
    """Create the logs directory if it doesn't exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


def _crash_excepthook(exc_type, exc_value, exc_traceback) -> None:
    """Custom excepthook that logs unhandled exceptions to the main log."""
    try:
        logger = get_logger("UNHANDLED")
        logger.critical(
            "Unhandled exception (process will exit)",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _crash_unraisablehook(unraisable) -> None:
    """Custom unraisablehook that logs unraisable exceptions to the main log."""
    if unraisable.exc_type is not None:
        try:
            logger = get_logger("UNHANDLED")
            logger.critical(
                "Unraisable exception in %s: %s",
                unraisable.object,
                unraisable.err_msg,
                exc_info=(
                    unraisable.exc_type,
                    unraisable.exc_value,
                    unraisable.exc_traceback,
                ),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    sys.__unraisablehook__(unraisable)


def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Configure the root logger and install crash-capture hooks.

    Sets up:
      - RotatingFileHandler writing to logs/snackattack.log (5 MB, 3 backups)
      - StreamHandler writing to stderr
      - sys.excepthook for unhandled exceptions
      - sys.unraisablehook for unraisable exceptions (Kivy can trigger these)

    Args:
        log_level: The minimum logging level. Defaults to logging.INFO.
    """
    # Ensure log directory exists
    _ensure_log_dir()

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates on re-initialization
    root_logger.handlers.clear()

    # --- File handler (rotating) ---
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_formatter = MillisecondFormatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # --- Console handler (use original stderr, bypassing Kivy's wrapper) ---
    console_handler = logging.StreamHandler(sys.__stderr__)
    console_handler.setLevel(log_level)
    console_formatter = MillisecondFormatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # --- Install crash-capture hooks ---
    sys.excepthook = _crash_excepthook
    sys.unraisablehook = _crash_unraisablehook

    # Log startup
    logger = get_logger(__name__)
    logger.info("Logging initialized (level=%s)", logging.getLevelName(log_level))
    logger.info("Log file: %s", os.path.abspath(LOG_FILE))


def get_all_log_file_paths() -> List[str]:
    """
    Get paths of all log files in the logs directory.

    Returns:
        List of file paths, with the main log first, then rotated
        backups (newest first).
    """
    paths = []

    main_log = os.path.join(LOG_DIR, "snackattack.log")
    if os.path.isfile(main_log):
        paths.append(main_log)

    # Rotated backups (snackattack.log.1, .2, .3) — most recent first
    for i in range(1, 4):
        backup = os.path.join(LOG_DIR, f"snackattack.log.{i}")
        if os.path.isfile(backup):
            paths.append(backup)

    return paths


def collect_all_logs() -> str:
    """
    Collect all log content into a single string with section headers.

    Reads snackattack.log and its rotated backups.
    Each file is preceded by a clear header line.

    Returns:
        The concatenated log text, or a message if no logs exist.
    """
    sections = []

    for file_path in get_all_log_file_paths():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            basename = os.path.basename(file_path)
            header = f"===== {basename} ====="
            sections.append(f"{header}\n{content}")
        except OSError as e:
            basename = os.path.basename(file_path)
            sections.append(f"===== {basename} =====\n[Error reading file: {e}]\n")

    if not sections:
        return "No log files found."

    return "\n\n".join(sections)
