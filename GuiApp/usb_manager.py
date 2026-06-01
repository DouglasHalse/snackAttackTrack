"""
USB Manager — handles detection of removable drives and copying log files.

Provides:
- USBManager: Class with detect_drives() and copy_logs() methods.
- Custom exceptions for fine-grained error handling.
"""

# pylint: disable=no-member
# OSError.winerror is Windows-only; guarded by hasattr() at runtime.
# But pylint's static analysis on Linux flags it as E1101.

import os
import platform
import re
import shutil
import subprocess
from typing import List, Optional, Tuple

from logger import get_logger


logger = get_logger(__name__)


class USBError(Exception):
    """Base exception for all USB-related errors."""


class NoUSBDeviceError(USBError):
    """Raised when no removable USB drive is detected."""


class USBCopyError(USBError):
    """Raised when copying one or more files fails."""


class USBPermissionError(USBError):
    """Raised when the destination drive is not writable."""


class USBDiskFullError(USBError):
    """Raised when the destination drive does not have enough space."""


class USBManager:
    """Manages detection of USB drives and copying files to them."""

    @staticmethod
    def _detect_windows_drives() -> List[str]:
        """Detect removable drives on Windows using GetDriveTypeW."""
        import ctypes  # pylint: disable=import-outside-toplevel

        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        logger.debug("Windows logical drives bitmask: %s", bin(bitmask))
        for letter_index in range(3, 26):
            if bitmask & (1 << letter_index):
                drive_letter = chr(ord("A") + letter_index)
                drive_root = f"{drive_letter}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_root)
                logger.debug(
                    "Drive %s: GetDriveTypeW() returned %d",
                    drive_root,
                    drive_type,
                )
                if drive_type == 2:  # DRIVE_REMOVABLE
                    drives.append(drive_root)
        return drives

    @staticmethod
    def _get_removable_block_devices() -> List[Tuple[str, Optional[str]]]:
        # pylint: disable=too-many-locals,too-many-branches
        """Scan /sys/block for removable devices and cross-reference /proc/mounts.

        Returns:
            List of (device_path, mount_point) tuples.
            mount_point is None if the device partition is not mounted.
        """
        devices: List[Tuple[str, Optional[str]]] = []

        # Read /proc/mounts into a dict: device -> mount_point
        mounts: dict[str, str] = {}
        try:
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        dev = parts[0]
                        mnt = parts[1]
                        mounts[dev] = mnt
        except OSError as e:
            logger.debug(
                "Cannot read /proc/mounts: %s — will rely on directory scan", e
            )

        # Find removable block devices
        sys_block = "/sys/block"
        if not os.path.isdir(sys_block):
            return devices

        try:
            for entry in os.listdir(sys_block):
                removable_path = os.path.join(sys_block, entry, "removable")
                if not os.path.isfile(removable_path):
                    continue
                try:
                    with open(removable_path, "r", encoding="utf-8") as f:
                        if f.read().strip() != "1":
                            continue  # Not removable
                except OSError:
                    continue

                logger.debug("Removable block device found: %s", entry)

                # Enumerate partitions (e.g. sda1, sda2 or mmcblk0p1)
                partitions = []
                for prefix in [f"{entry}p", entry]:
                    part_dir = os.path.join(sys_block, entry)
                    if not os.path.isdir(part_dir):
                        continue
                    try:
                        for sub in os.listdir(part_dir):
                            if sub.startswith(prefix) and os.path.isdir(
                                os.path.join(sys_block, entry, sub)
                            ):
                                dev_path = f"/dev/{sub}"
                                partitions.append((dev_path, mounts.get(dev_path)))
                    except OSError:
                        continue

                if partitions:
                    devices.extend(partitions)
                    for dev_path, mnt in partitions:
                        logger.debug(
                            "  Partition %s -> mount: %s",
                            dev_path,
                            mnt or "(not mounted)",
                        )
                else:
                    base_dev = f"/dev/{entry}"
                    mnt = mounts.get(base_dev)
                    devices.append((base_dev, mnt))
                    logger.debug(
                        "  Whole device %s -> mount: %s",
                        base_dev,
                        mnt or "(not mounted)",
                    )
        except OSError as e:
            logger.debug("Cannot scan /sys/block: %s", e)

        return devices

    @staticmethod
    def _is_writable_mount(path: str) -> bool:
        """Check if a mount point is writable by attempting a real file write.

        Args:
            path: The directory to test.

        Returns:
            True if a test file was successfully created and removed.
        """
        test_file = os.path.join(path, ".snackattack_write_test")
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(test_file)
            return True
        except (PermissionError, OSError) as e:
            logger.debug("Mount %s is not writable: %s", path, e)
            return False

    @staticmethod
    def _resolve_mount_point(device_path: str) -> Optional[str]:
        """Find the mount point for a device by re-reading /proc/mounts.

        Args:
            device_path: The device path (e.g. /dev/sda1).

        Returns:
            The mount point path, or None if not found.
        """
        try:
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == device_path:
                        return parts[1]
        except OSError:
            pass
        return None

    @staticmethod
    def _auto_mount_drive(device_path: str) -> str:
        """Mount a removable device using udisksctl (udisks2).

        udisks2 is the standard Linux disk management service. On Raspberry Pi
        it is installed by the setup script (setup.sh) and
        works without sudo via polkit for the local console user.

        Args:
            device_path: The device path to mount (e.g. /dev/sda1).

        Returns:
            The mount point path where the device was mounted.

        Raises:
            NoUSBDeviceError: If udisks2 is not installed or mounting fails.
        """
        if not shutil.which("udisksctl"):
            raise NoUSBDeviceError(
                "USB drive detected but could not be mounted automatically. "
                "Please run the setup script: 'bash setup.sh'"
            )

        logger.debug("Mounting %s via udisksctl", device_path)
        try:
            result = subprocess.run(
                ["udisksctl", "mount", "-b", device_path, "--no-user-interaction"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            raise NoUSBDeviceError(f"Failed to mount USB drive: {e}") from e

        if result.returncode != 0:
            raise NoUSBDeviceError(
                f"Failed to mount USB drive: " f"{result.stderr.strip()}"
            )

        # Parse output: "Mounted /dev/sda1 at /media/pi/KINGSTON."
        match = re.search(r"at\s+(/.+?)\.?\s*$", result.stdout)
        if match:
            mount_point = match.group(1).strip()
            logger.info("Mounted %s at %s", device_path, mount_point)
            return mount_point

        # Fallback: re-check /proc/mounts
        mount_point = USBManager._resolve_mount_point(device_path)
        if mount_point:
            logger.info(
                "Mounted %s at %s (from /proc/mounts)",
                device_path,
                mount_point,
            )
            return mount_point

        raise NoUSBDeviceError(
            f"USB drive was mounted but could not determine mount point. "
            f"Output: {result.stdout.strip()}"
        )

    @staticmethod
    def _scan_mount_directories_fallback() -> List[str]:
        # pylint: disable=too-many-nested-blocks
        """Fallback: scan common mount directories up to 2 levels deep.

        Returns:
            List of writable mount point paths found.
        """
        candidates: List[str] = []
        search_paths = ["/media", "/mnt", "/run/media"]
        for base_path in search_paths:
            if not os.path.isdir(base_path):
                continue
            try:
                for entry in os.listdir(base_path):
                    level1 = os.path.join(base_path, entry)
                    if not os.path.isdir(level1):
                        continue
                    if os.path.ismount(level1) and USBManager._is_writable_mount(
                        level1
                    ):
                        candidates.append(level1)
                        continue
                    try:
                        for sub in os.listdir(level1):
                            level2 = os.path.join(level1, sub)
                            if os.path.isdir(level2) and os.path.ismount(level2):
                                if USBManager._is_writable_mount(level2):
                                    candidates.append(level2)
                    except PermissionError:
                        continue
            except PermissionError:
                continue
        return candidates

    @staticmethod
    def _detect_and_mount_linux_drives() -> List[str]:
        # pylint: disable=too-many-branches,too-many-nested-blocks
        """Detect and optionally auto-mount removable drives on Linux.

        1. Enumerate removable block devices via /sys/block + /proc/mounts.
        2. If already mounted and writable, use as-is.
        3. If not mounted, attempt auto-mount via udisksctl.
        4. Fallback: scan common mount directories.

        Returns:
            List of writable mount point paths.

        Raises:
            NoUSBDeviceError: If no drives found or all mount attempts fail.
        """
        candidates: List[str] = []

        block_devices = USBManager._get_removable_block_devices()
        logger.debug(
            "Removable block devices detected: %s",
            [d for d, _ in block_devices],
        )

        any_unmounted = False
        for device_path, mount_point in block_devices:
            if mount_point:
                if USBManager._is_writable_mount(mount_point):
                    candidates.append(mount_point)
                    logger.debug(
                        "Using already-mounted drive: %s at %s",
                        device_path,
                        mount_point,
                    )
                else:
                    logger.warning(
                        "Drive %s is mounted at %s but is not writable — skipping",
                        device_path,
                        mount_point,
                    )
            else:
                any_unmounted = True
                logger.debug("Attempting to auto-mount %s", device_path)
                try:
                    mnt = USBManager._auto_mount_drive(device_path)
                    if USBManager._is_writable_mount(mnt):
                        candidates.append(mnt)
                        logger.info("Auto-mounted: %s at %s", device_path, mnt)
                    else:
                        logger.warning(
                            "Auto-mounted %s at %s but it is not writable",
                            device_path,
                            mnt,
                        )
                except NoUSBDeviceError:
                    logger.debug(
                        "Failed to auto-mount %s — all methods exhausted",
                        device_path,
                    )

        if not candidates:
            fallback = USBManager._scan_mount_directories_fallback()
            seen = {os.path.realpath(c) for c in candidates}
            for fb in fallback:
                if os.path.realpath(fb) not in seen:
                    candidates.append(fb)
                    seen.add(os.path.realpath(fb))

        if not candidates:
            if any_unmounted or block_devices:
                raise NoUSBDeviceError(
                    "USB drive detected but could not be mounted automatically. "
                    "Please run the setup script: 'bash setup.sh'"
                )
            raise NoUSBDeviceError(
                "No USB drive detected. Please insert a USB drive and try again."
            )

        return candidates

    @staticmethod
    def detect_drives() -> List[str]:
        """
        Detect connected removable USB drives.

        On Linux, uses /sys/block + /proc/mounts for accurate detection
        and auto-mounts unmounted drives via udisksctl / pmount / sudo.

        Returns:
            List of paths to detected removable drive roots.

        Raises:
            NoUSBDeviceError: If no removable drives are found.
        """
        if platform.system() == "Windows":
            drives = USBManager._detect_windows_drives()
        else:
            drives = USBManager._detect_and_mount_linux_drives()

        if not drives:
            raise NoUSBDeviceError(
                "No removable USB drive detected. Please insert a USB drive and try again."
            )

        return drives

    @staticmethod
    def copy_logs(file_paths: List[str], target_drive: str) -> int:
        """
        Copy log files to a target directory on the USB drive.

        Args:
            file_paths: List of source file paths to copy.
            target_drive: Root path of the USB drive (e.g. 'E:\\' or '/media/usb0').

        Returns:
            The number of files successfully copied.

        Raises:
            USBPermissionError: If the target drive is not writable.
            USBDiskFullError: If there is not enough space on the target.
            USBCopyError: If a file copy fails for any other reason.
        """
        target_dir = os.path.join(target_drive, "snackattack_logs")

        # Check if the drive is writable (using real file write, not os.access)
        if not USBManager._is_writable_mount(target_drive):
            raise USBPermissionError(
                f"The USB drive at {target_drive} is not writable. "
                "Check permissions and ensure the drive is not write-protected."
            )

        try:
            os.makedirs(target_dir, exist_ok=True)
        except PermissionError as e:
            raise USBPermissionError(
                f"Cannot create target directory on USB drive: {e}"
            ) from e
        except OSError as e:
            raise USBCopyError(
                f"Failed to create target directory on USB drive: {e}"
            ) from e

        copied_count = 0
        for src_path in file_paths:
            dst_path = os.path.join(target_dir, os.path.basename(src_path))
            try:
                shutil.copy2(src_path, dst_path)
                copied_count += 1
            except PermissionError as e:
                raise USBPermissionError(
                    f"Permission denied when copying {os.path.basename(src_path)}: {e}"
                ) from e
            except OSError as e:
                # Check for disk-full condition (Windows: 112, Linux: errno.ENOSPC)
                if (hasattr(e, "winerror") and e.winerror == 112) or (
                    hasattr(e, "errno") and e.errno == 28
                ):
                    raise USBDiskFullError(
                        f"The USB drive at {target_drive} does not have enough space "
                        f"to copy the log files. Free up space and try again."
                    ) from e
                raise USBCopyError(
                    f"Failed to copy {os.path.basename(src_path)}: {e}"
                ) from e

        logger.info("Copied %d log files to USB drive at %s", copied_count, target_dir)
        return copied_count

    @staticmethod
    def detect_and_copy(file_paths: List[str]) -> str:
        """
        Convenience method: detect the first USB drive and copy logs to it.

        Args:
            file_paths: List of source file paths to copy.

        Returns:
            The destination directory path where files were copied.

        Raises:
            NoUSBDeviceError: If no removable drive is detected.
            USBPermissionError: If the drive is not writable.
            USBDiskFullError: If the drive is full.
            USBCopyError: If copying fails.
        """
        drives = USBManager.detect_drives()
        target_drive = drives[0]
        USBManager.copy_logs(file_paths, target_drive)
        return os.path.join(target_drive, "snackattack_logs")
