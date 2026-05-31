"""
Tests for the USB manager module (usb_manager.py).

All tests are non-Kivy, function-scoped, and use tmp_path for isolation.
"""

import errno
import os
import shutil
import subprocess
from io import StringIO

import pytest

from usb_manager import (
    USBManager,
    USBError,
    NoUSBDeviceError,
    USBPermissionError,
    USBDiskFullError,
    USBCopyError,
)


class TestUSBExceptions:
    """Verify the exception hierarchy."""

    def test_all_exceptions_inherit_from_usb_error(self):
        """Every USB exception should be catchable as USBError."""
        assert issubclass(NoUSBDeviceError, USBError)
        assert issubclass(USBPermissionError, USBError)
        assert issubclass(USBDiskFullError, USBError)
        assert issubclass(USBCopyError, USBError)


class TestCopyLogs:
    """Test the copy_logs static method directly."""

    @pytest.fixture
    def source_files(self, tmp_path):
        """Create a few test log files to copy."""
        src = tmp_path / "source"
        src.mkdir()
        (src / "snackattack.log").write_text("line1\nline2\n")
        (src / "snackattack.log.1").write_text("old\n")
        return [str(src / "snackattack.log"), str(src / "snackattack.log.1")]

    @pytest.fixture
    def target_dir(self, tmp_path):
        """Return a writable target directory path."""
        tgt = tmp_path / "usb_drive"
        tgt.mkdir()
        return str(tgt)

    def test_copy_logs_copies_files(self, source_files, target_dir):
        """Files should be copied and correct count returned."""
        count = USBManager.copy_logs(source_files, target_dir)
        assert count == 2
        assert os.path.isfile(
            os.path.join(target_dir, "snackattack_logs", "snackattack.log")
        )
        assert os.path.isfile(
            os.path.join(target_dir, "snackattack_logs", "snackattack.log.1")
        )

    def test_copy_logs_raises_permission_error(
        self, source_files, tmp_path, monkeypatch
    ):
        """Unwritable target should raise USBPermissionError."""
        unwritable = tmp_path / "unwritable"
        unwritable.mkdir()

        # Mock _is_writable_mount to simulate a non-writable directory
        monkeypatch.setattr(USBManager, "_is_writable_mount", lambda path: False)

        with pytest.raises(USBPermissionError):
            USBManager.copy_logs(source_files, str(unwritable))

    def test_copy_logs_raises_copy_error(self, source_files, target_dir, monkeypatch):
        """A generic OSError during copy should raise USBCopyError."""

        def failing_copy2(src, dst, *args, **kwargs):
            raise OSError("Connection broke")

        monkeypatch.setattr(shutil, "copy2", failing_copy2)

        with pytest.raises(USBCopyError):
            USBManager.copy_logs(source_files, target_dir)

    def test_copy_logs_raises_disk_full(self, source_files, target_dir, monkeypatch):
        """An OSError with errno.ENOSPC should raise USBDiskFullError."""

        def failing_copy2(src, dst, *args, **kwargs):
            raise OSError(errno.ENOSPC, "No space left on device")

        monkeypatch.setattr(shutil, "copy2", failing_copy2)

        with pytest.raises(USBDiskFullError):
            USBManager.copy_logs(source_files, target_dir)


class TestDetectDrives:
    """Test the detect_drives static method."""

    def test_detect_drives_raises_if_none_found(self, monkeypatch):
        """When no drives are detected, NoUSBDeviceError should be raised."""
        # Mock platform to Linux so we scan /media etc.
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr("os.path.isdir", lambda p: False)

        with pytest.raises(NoUSBDeviceError):
            USBManager.detect_drives()


class TestDetectAndCopy:
    """Test the combined detect_and_copy method."""

    def test_detect_and_copy_raises_no_device(self, monkeypatch):
        """When no drive is detected, NoUSBDeviceError should propagate."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr("os.path.isdir", lambda p: False)

        with pytest.raises(NoUSBDeviceError):
            USBManager.detect_and_copy([])


class TestIsWritableMount:
    """Test the _is_writable_mount static method."""

    # pylint: disable=protected-access

    def test_writable_directory(self, tmp_path):
        """A writable directory should return True."""
        assert USBManager._is_writable_mount(str(tmp_path))

    def test_unwritable_directory(self, tmp_path, monkeypatch):
        """An unwritable directory should return False."""
        # Mock open to fail with PermissionError
        def failing_open(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr("builtins.open", failing_open)
        assert not USBManager._is_writable_mount(str(tmp_path))


class TestResolveMountPoint:
    """Test the _resolve_mount_point static method."""

    # pylint: disable=protected-access

    def test_device_found(self, monkeypatch):
        """A device listed in /proc/mounts should return its mount point."""
        original_open = open

        def mock_open(path, *a, **kw):
            normalized = path.replace("\\", "/")
            if normalized == "/proc/mounts":
                return StringIO(
                    "/dev/sda1 /media/pi/USB vfat rw,relatime 0 0\n"
                    "/dev/mmcblk0p2 / ext4 rw,relatime 0 0\n"
                )
            return original_open(path, *a, **kw)

        monkeypatch.setattr("builtins.open", mock_open)
        result = USBManager._resolve_mount_point("/dev/sda1")
        assert result == "/media/pi/USB"

    def test_device_not_found(self, monkeypatch):
        """A device not in /proc/mounts should return None."""
        original_open = open

        def mock_open(path, *a, **kw):
            normalized = path.replace("\\", "/")
            if normalized == "/proc/mounts":
                return StringIO("/dev/mmcblk0p2 / ext4 rw,relatime 0 0\n")
            return original_open(path, *a, **kw)

        monkeypatch.setattr("builtins.open", mock_open)
        result = USBManager._resolve_mount_point("/dev/sdb1")
        assert result is None


class TestGetRemovableBlockDevices:
    """Test the _get_removable_block_devices static method."""

    # pylint: disable=protected-access

    def test_removable_mounted(self, monkeypatch):
        """Removable device that is mounted should appear with mount point."""
        original_open = open

        def mock_open(path, *a, **kw):
            normalized = path.replace("\\", "/")
            if normalized.endswith("removable"):
                return StringIO("1\n")
            if normalized == "/proc/mounts":
                return StringIO("/dev/sda1 /media/pi/USB vfat rw 0 0\n")
            return original_open(path, *a, **kw)

        monkeypatch.setattr("builtins.open", mock_open)
        monkeypatch.setattr(
            "os.listdir", lambda p: (["sda"] if p.endswith("block") else ["sda1"])
        )
        monkeypatch.setattr("os.path.isdir", lambda p: True)
        monkeypatch.setattr("os.path.isfile", lambda p: p.endswith("removable"))

        devices = USBManager._get_removable_block_devices()
        assert ("/dev/sda1", "/media/pi/USB") in devices

    def test_removable_not_mounted(self, monkeypatch):
        """Removable device that is not mounted should have None mount."""
        original_open = open

        def mock_open(path, *a, **kw):
            normalized = path.replace("\\", "/")
            if normalized.endswith("removable"):
                return StringIO("1\n")
            if normalized == "/proc/mounts":
                return StringIO("/dev/mmcblk0p2 / ext4 rw 0 0\n")
            return original_open(path, *a, **kw)

        monkeypatch.setattr("builtins.open", mock_open)
        monkeypatch.setattr(
            "os.listdir", lambda p: (["sda"] if p.endswith("block") else ["sda1"])
        )
        monkeypatch.setattr("os.path.isdir", lambda p: True)
        monkeypatch.setattr("os.path.isfile", lambda p: p.endswith("removable"))

        devices = USBManager._get_removable_block_devices()
        assert ("/dev/sda1", None) in devices

    def test_internal_drive_ignored(self, monkeypatch):
        """Internal drives (removable=0) should not appear in results."""
        original_open = open

        def mock_open(path, *a, **kw):
            normalized = path.replace("\\", "/")
            if normalized.endswith("removable"):
                return StringIO("0\n")  # Not removable
            return original_open(path, *a, **kw)

        monkeypatch.setattr("builtins.open", mock_open)
        monkeypatch.setattr(
            "os.listdir", lambda p: (["mmcblk0"] if p.endswith("block") else [])
        )
        monkeypatch.setattr("os.path.isdir", lambda p: True)
        monkeypatch.setattr("os.path.isfile", lambda p: p.endswith("removable"))

        devices = USBManager._get_removable_block_devices()
        assert len(devices) == 0


class TestAutoMountDrive:
    """Test the _auto_mount_drive static method."""

    # pylint: disable=protected-access

    def test_udisksctl_success(self, monkeypatch):
        """udisksctl should return the parsed mount point."""
        monkeypatch.setattr(
            shutil,
            "which",
            lambda cmd: "/usr/bin/udisksctl" if cmd == "udisksctl" else None,
        )

        class FakeResult:
            returncode = 0
            stdout = "Mounted /dev/sda1 at /media/pi/KINGSTON.\n"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
        monkeypatch.setattr(USBManager, "_resolve_mount_point", lambda d: None)

        result = USBManager._auto_mount_drive("/dev/sda1")
        assert result == "/media/pi/KINGSTON"

    def test_skips_parse_and_uses_proc_mounts(self, monkeypatch):
        """When stdout parsing fails, _resolve_mount_point fallback should work."""
        monkeypatch.setattr(
            shutil,
            "which",
            lambda cmd: "/usr/bin/udisksctl" if cmd == "udisksctl" else None,
        )

        class FakeResult:
            returncode = 0
            stdout = "Mounted /dev/sda1\n"  # No "at /path" pattern
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
        monkeypatch.setattr(
            USBManager, "_resolve_mount_point", lambda d: "/media/pi/USB"
        )

        result = USBManager._auto_mount_drive("/dev/sda1")
        assert result == "/media/pi/USB"

    def test_raises_when_udisksctl_not_installed(self, monkeypatch):
        """When udisksctl is not available, NoUSBDeviceError should be raised."""
        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        with pytest.raises(NoUSBDeviceError) as exc:
            USBManager._auto_mount_drive("/dev/sda1")
        assert "setupDevEnvironmentUbuntu.sh" in str(exc.value)

    def test_raises_when_mount_fails(self, monkeypatch):
        """When udisksctl returns non-zero, NoUSBDeviceError should be raised."""
        monkeypatch.setattr(
            shutil,
            "which",
            lambda cmd: "/usr/bin/udisksctl" if cmd == "udisksctl" else None,
        )

        class FakeResult:
            returncode = 1
            stdout = ""
            stderr = "Permission denied"

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())

        with pytest.raises(NoUSBDeviceError) as exc:
            USBManager._auto_mount_drive("/dev/sda1")
        assert "Permission denied" in str(exc.value)


class TestScanMountDirectoriesFallback:
    """Test the _scan_mount_directories_fallback static method."""

    # pylint: disable=protected-access

    def test_finds_writable_mount(self, monkeypatch):
        """A writable mount at 2-level depth should be found."""

        def fake_listdir(path):
            normalized = path.replace("\\", "/")
            if normalized == "/media":
                return ["pi"]
            if normalized == "/media/pi":
                return ["KINGSTON"]
            return []

        monkeypatch.setattr("os.listdir", fake_listdir)
        monkeypatch.setattr("os.path.isdir", lambda p: True)
        monkeypatch.setattr(
            "os.path.ismount",
            lambda p: (
                p.replace("\\", "/").endswith("KINGSTON")
                or p.replace("\\", "/").endswith("/media/pi/KINGSTON")
            ),
        )
        monkeypatch.setattr(
            USBManager,
            "_is_writable_mount",
            lambda p: p.replace("\\", "/").endswith("KINGSTON"),
        )

        result = USBManager._scan_mount_directories_fallback()
        assert any(p.replace("\\", "/").endswith("KINGSTON") for p in result)

    def test_returns_empty_when_no_mounts(self, monkeypatch):
        """When no writable mounts exist, an empty list should be returned."""
        monkeypatch.setattr("os.path.isdir", lambda p: False)
        result = USBManager._scan_mount_directories_fallback()
        assert result == []


class TestDetectAndMountLinuxDrives:
    """Test the _detect_and_mount_linux_drives static method."""

    # pylint: disable=protected-access

    def test_uses_already_mounted(self, monkeypatch):
        """An already-mounted writable drive should be used directly."""
        monkeypatch.setattr(
            USBManager,
            "_get_removable_block_devices",
            lambda: [("/dev/sda1", "/media/pi/USB")],
        )
        monkeypatch.setattr(USBManager, "_is_writable_mount", lambda p: True)
        monkeypatch.setattr(USBManager, "_scan_mount_directories_fallback", lambda: [])

        result = USBManager._detect_and_mount_linux_drives()
        assert "/media/pi/USB" in result

    def test_auto_mounts_unmounted(self, monkeypatch):
        """An unmounted removable device should be auto-mounted."""
        monkeypatch.setattr(
            USBManager,
            "_get_removable_block_devices",
            lambda: [("/dev/sda1", None)],
        )
        monkeypatch.setattr(
            USBManager,
            "_auto_mount_drive",
            lambda d: "/media/pi/AUTOMOUNT",
        )
        monkeypatch.setattr(USBManager, "_is_writable_mount", lambda p: True)
        monkeypatch.setattr(USBManager, "_scan_mount_directories_fallback", lambda: [])

        result = USBManager._detect_and_mount_linux_drives()
        assert "/media/pi/AUTOMOUNT" in result

    def test_raises_no_device_when_none_found(self, monkeypatch):
        """When no removable devices exist, NoUSBDeviceError should be raised."""
        monkeypatch.setattr(USBManager, "_get_removable_block_devices", lambda: [])
        monkeypatch.setattr(USBManager, "_scan_mount_directories_fallback", lambda: [])

        with pytest.raises(NoUSBDeviceError) as exc:
            USBManager._detect_and_mount_linux_drives()
        assert "No USB drive detected" in str(exc.value)

    def test_raises_when_all_mount_attempts_fail(self, monkeypatch):
        """When devices exist but auto-mount fails, should suggest setup script."""
        monkeypatch.setattr(
            USBManager,
            "_get_removable_block_devices",
            lambda: [("/dev/sda1", None)],
        )
        monkeypatch.setattr(
            USBManager,
            "_auto_mount_drive",
            lambda d: (_ for _ in ()).throw(
                NoUSBDeviceError(
                    "USB drive detected but could not be mounted automatically. "
                    "Please run the setup script: 'bash setupDevEnvironmentUbuntu.sh'"
                )
            ),
        )
        monkeypatch.setattr(USBManager, "_scan_mount_directories_fallback", lambda: [])

        with pytest.raises(NoUSBDeviceError) as exc:
            USBManager._detect_and_mount_linux_drives()
        assert "setupDevEnvironmentUbuntu.sh" in str(exc.value)


class TestDetectDrivesLinux:
    """Test detect_drives on Linux (integration-style with mocks)."""

    # pylint: disable=protected-access

    def test_detect_drives_linux_success(self, monkeypatch):
        """When Linux detection finds drives, detect_drives should return them."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr(
            USBManager,
            "_detect_and_mount_linux_drives",
            lambda: ["/media/pi/USB"],
        )

        result = USBManager.detect_drives()
        assert "/media/pi/USB" in result

    def test_detect_drives_linux_raises(self, monkeypatch):
        """When Linux detection fails, NoUSBDeviceError should be raised."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr(
            USBManager,
            "_detect_and_mount_linux_drives",
            lambda: (_ for _ in ()).throw(
                NoUSBDeviceError(
                    "No USB drive detected. Please insert a USB drive and try again."
                )
            ),
        )

        with pytest.raises(NoUSBDeviceError) as exc:
            USBManager.detect_drives()
        assert "No USB drive detected" in str(exc.value)
