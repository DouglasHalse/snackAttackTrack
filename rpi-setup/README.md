# Raspberry Pi Setup Files

This directory contains scripts and documentation for deploying SnackAttack on Raspberry Pi hardware with automatic boot configuration.

## Files

### `quick-deploy.sh` ⚡
**One-command deployment script** - Run this on a fresh Raspberry Pi OS Lite installation to automatically configure everything.

**Usage:**
```bash
cd /home/pi
git clone https://github.com/DouglasHalse/snackAttackTrack.git
cd snackAttackTrack/rpi-setup
chmod +x quick-deploy.sh
./quick-deploy.sh
sudo reboot
```

**What it does:**
- Updates system packages
- Installs all dependencies (SDL2, Python libraries, X server)
- Configures auto-login to console
- Sets up X server with matchbox window manager
- Configures SnackAttack to launch on boot
- Creates helper scripts for maintenance
- Sets up log rotation

### `setup-autostart.sh`
**Detailed auto-start configuration** - More verbose version with step-by-step explanations.

**Usage:**
```bash
cd /home/pi/snackAttackTrack
chmod +x rpi-setup/setup-autostart.sh
./rpi-setup/setup-autostart.sh
sudo reboot
```

### `create-custom-image.md` 📖
**Complete guide** for creating a custom Raspberry Pi image that can be flashed to multiple devices.

**Covers:**
- Initial OS setup and configuration
- Creating bootable images with SnackAttack pre-installed
- Customization options (display resolution, touchscreen, performance)
- Troubleshooting common issues
- Security hardening
- Maintenance procedures

## Quick Start

### Accessing Your Raspberry Pi

**From Windows:** Use SSH to connect to your Raspberry Pi:
1. Enable SSH during image flashing (Raspberry Pi Imager settings)
2. Find Pi's IP address (check your router or use `ping raspberrypi.local`)
3. Connect:
   ```powershell
   ssh pi@raspberrypi.local
   # or
   ssh pi@<IP_ADDRESS>
   ```
4. Run the setup commands below **on the Pi**, not on Windows

**Direct Access:** Connect keyboard/monitor to Pi and login directly

### Option 1: Automated Setup (Recommended)

> **Note:** Run these commands **on the Raspberry Pi** (SSH or direct terminal), not on Windows.

1. Flash Raspberry Pi OS Lite to SD card
2. Boot and login (or SSH into the Pi)
3. Run:
   ```bash
   curl -sSL https://raw.githubusercontent.com/DouglasHalse/snackAttackTrack/main/rpi-setup/quick-deploy.sh | bash
   ```
   
   Or download and run manually:
   ```bash
   wget https://raw.githubusercontent.com/DouglasHalse/snackAttackTrack/main/rpi-setup/quick-deploy.sh
   chmod +x quick-deploy.sh
   ./quick-deploy.sh
   ```
4. Reboot

### Option 2: Manual Setup

Follow the step-by-step guide in `create-custom-image.md`

### Option 3: Test in VMware/VirtualBox First

Want to test without a Raspberry Pi? See [testing-with-vmware.md](testing-with-vmware.md) for:
- Setting up test environment in VMware or VirtualBox
- Testing with Debian/Ubuntu (faster than Pi emulation)
- Simulating touchscreen and workflows
- Creating team testing environments

## System Requirements

- **Hardware:** Raspberry Pi 3B+ or newer (4GB RAM recommended)
- **OS:** Raspberry Pi OS Lite (Bookworm) - 64-bit recommended
- **Storage:** 8GB+ SD card (16GB+ recommended)
- **Display:** HDMI display or official touchscreen
- **Network:** WiFi or Ethernet for initial setup

## Architecture

### Boot Sequence
```
1. Raspberry Pi boots → Raspberry Pi OS Lite
2. Auto-login as 'pi' user → Console (tty1)
3. .bash_profile triggers → startx
4. .xinitrc executes:
   ├── Disable screen blanking (xset)
   ├── Hide cursor (unclutter)
   ├── Start window manager (matchbox)
   └── Launch SnackAttack (python3 main.py)
```

### Why This Approach?

**Raspberry Pi OS Lite benefits:**
- ✅ Minimal resource usage (~200MB RAM vs 1GB+ with desktop)
- ✅ Fast boot time (~10-15 seconds to app launch)
- ✅ No unnecessary desktop environment services
- ✅ Direct framebuffer rendering for better graphics performance
- ✅ Longer SD card lifespan (fewer writes)

**X Server with Matchbox:**
- ✅ Provides OpenGL/GLX support required by Kivy
- ✅ Matchbox is extremely lightweight (~5MB memory)
- ✅ No window decorations = cleaner kiosk mode
- ✅ Better touch input handling than pure framebuffer

## Helper Scripts

After installation, the following scripts are available in `/home/pi/`:

### `restart-snackattack.sh`
Restart the application without rebooting:
```bash
~/restart-snackattack.sh
```

### `update-snackattack.sh`
Pull latest changes from git and restart:
```bash
~/update-snackattack.sh
```

### `stop-snackattack.sh`
Stop the application and return to console:
```bash
~/stop-snackattack.sh
```

## Configuration

### Display Settings

Edit `/boot/config.txt` to adjust display output:

```bash
sudo nano /boot/config.txt
```

**Common configurations:**

**HDMI Display:**
```ini
hdmi_force_hotplug=1
hdmi_drive=2
hdmi_group=2
hdmi_mode=82  # 1920x1080 60Hz
disable_overscan=1
```

**Official 7" Touchscreen:**
```ini
lcd_rotate=2  # 0, 2 for orientation
disable_overscan=1
```

**Performance Tuning:**
```ini
gpu_mem=256
arm_freq=1800  # Overclock (ensure adequate cooling)
```

### WiFi Configuration

If you need to update WiFi credentials after deployment:

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add network:
```
network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

## Troubleshooting

### App doesn't start after reboot

1. Check if X is running:
   ```bash
   ps aux | grep X
   ```

2. View startup logs:
   ```bash
   cat ~/snackattack.log
   ```

3. Test manual launch:
   ```bash
   cd /home/pi/snackAttackTrack/GuiApp
   python3 main.py
   ```

### Display shows wrong resolution

Edit `/boot/config.txt` and set appropriate hdmi_mode:
```bash
sudo nano /boot/config.txt
```

Common modes:
- `hdmi_mode=4`: 1280x720 60Hz
- `hdmi_mode=16`: 1024x768 60Hz  
- `hdmi_mode=82`: 1920x1080 60Hz

### Touch not working

Install input drivers:
```bash
sudo apt-get install python3-evdev
```

Check input devices:
```bash
ls -l /dev/input/
```

### Performance issues

1. Check temperature:
   ```bash
   vcgencmd measure_temp
   ```

2. Increase GPU memory in `/boot/config.txt`:
   ```ini
   gpu_mem=256
   ```

3. Disable unnecessary services:
   ```bash
   sudo systemctl disable bluetooth
   ```

## Creating Distributable Images

Once you have a working setup:

1. **On the Pi:** Shutdown cleanly
   ```bash
   sudo shutdown -h now
   ```

2. **On your computer:** Create image from SD card
   
   **Linux:**
   ```bash
   sudo dd if=/dev/sdX of=snackattack-rpi.img bs=4M status=progress
   ```
   
   **macOS:**
   ```bash
   sudo dd if=/dev/diskX of=snackattack-rpi.img bs=4m
   ```
   
   **Windows:**
   - Use Win32 Disk Imager

3. **Shrink image** (Linux only):
   ```bash
   wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
   chmod +x pishrink.sh
   sudo ./pishrink.sh snackattack-rpi.img
   ```

4. **Compress:**
   ```bash
   gzip snackattack-rpi.img
   ```

## Security Notes

1. **Change default password** after first boot:
   ```bash
   passwd
   ```

2. **Disable SSH** if not needed:
   ```bash
   sudo systemctl disable ssh
   ```

3. **Enable firewall** for network deployments:
   ```bash
   sudo apt-get install ufw
   sudo ufw allow ssh
   sudo ufw enable
   ```

4. **Keep system updated:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

## Support

For issues specific to Raspberry Pi deployment, check:
- Raspberry Pi forums: https://forums.raspberrypi.com/
- Kivy on RPi: https://kivy.org/doc/stable/installation/installation-rpi.html
- SnackAttack issues: https://github.com/DouglasHalse/snackAttackTrack/issues

## License

These deployment scripts are part of the SnackAttack project and follow the same license.
