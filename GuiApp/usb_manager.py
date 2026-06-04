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


def _run_mount_cmd(cmd: List[str]) -> Optional[str]:
    """Run a mount command via subprocess, returning stderr on failure or None on success."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return None
        return result.stderr.strip() or result.stdout.strip() or "no output"
    except OSError as e:
        return str(e)


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
    def _try_mount_drive(device_path: str) -> Tuple[Optional[str], str]:
        """Mount a USB drive."""
        target = "/mnt/snackattack_usb"
        cmd = f"sudo mkdir -p {target} && sudo mount {device_path} {target}"
        logger.info("Running: %s", cmd)
        rc = os.system(cmd)
        if rc == 0:
            logger.info("Mounted %s at %s", device_path, target)
            return target, ""
        return None, f"mount failed (exit code {rc})"

    @staticmethod
    def _detect_linux_drives() -> List[str]:
        # pylint: disable=too-many-branches
        """Detect connected removable USB drives on Linux.

        USB drives are auto-mounted by a udev rule (installed by
        setup_pi.sh) to /media/snackattack_usb when inserted.
        This method finds drives that are already mounted.

        Returns:
            List of writable mount point paths.

        Raises:
            NoUSBDeviceError: If no mounted removable drives are found.
        """
        candidates: List[str] = []

        block_devices = USBManager._get_removable_block_devices()
        logger.debug(
            "Removable block devices detected: %s",
            [d for d, _ in block_devices],
        )

        unmounted_devices = []
        last_mount_error = ""
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
                unmounted_devices.append(device_path)
                mnt, err = USBManager._try_mount_drive(device_path)
                if mnt and USBManager._is_writable_mount(mnt):
                    candidates.append(mnt)
                    logger.info("Mounted %s at %s", device_path, mnt)
                else:
                    last_mount_error = err or "unknown error"
                    logger.warning(
                        "Could not mount %s: %s", device_path, last_mount_error
                    )

        if not candidates:
            fallback = USBManager._scan_mount_directories_fallback()
            seen = {os.path.realpath(c) for c in candidates}
            for fb in fallback:
                if os.path.realpath(fb) not in seen:
                    candidates.append(fb)
                    seen.add(os.path.realpath(fb))

        if not candidates:
            info = f"Devices detected: {unmounted_devices or 'none'}. "
            if unmounted_devices:
                info += f"Mount failed: {last_mount_error}. "
                info += "Try 'sudo mount DEVICE /media/snackattack_usb' manually."
            else:
                info += "Insert a USB drive and try again."
            raise NoUSBDeviceError(info)

        return candidates

    @staticmethod
    def detect_drives() -> List[str]:
        """
        Detect connected removable USB drives.

        On Linux, uses /sys/block + /proc/mounts to find already-mounted
        removable drives, and attempts sudo mount for unmounted ones.

        Returns:
            List of paths to detected removable drive roots.

        Raises:
            NoUSBDeviceError: If no removable drives are found.
        """
        if platform.system() == "Windows":
            drives = USBManager._detect_windows_drives()
        else:
            drives = USBManager._detect_linux_drives()

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
