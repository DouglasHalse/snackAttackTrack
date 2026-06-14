# Creating a Custom Raspberry Pi Image for SnackAttack

This guide explains how to create a custom Raspberry Pi OS Lite image that automatically boots into SnackAttack.

## Prerequisites

- Raspberry Pi (3B+ or newer recommended)
- microSD card (16GB or larger)
- Computer with SD card reader
- Internet connection

## Step 1: Flash Base Image

### On Windows:

1. **Download Raspberry Pi OS Lite**
   - Go to https://www.raspberrypi.com/software/operating-systems/
   - Download "Raspberry Pi OS Lite (64-bit)" for better performance
   - Or use 32-bit if you have an older Pi

2. **Flash to SD Card using Raspberry Pi Imager**
   - Download from https://www.raspberrypi.com/software/
   - Select "Raspberry Pi OS Lite" as the OS
   - Select your SD card
   - Click settings (gear icon) and configure:
     - ✅ **Enable SSH** (important for remote access)
     - Set username: `pi`
     - Set password (choose a secure password)
     - Configure WiFi (optional but recommended for SSH access)
     - Set locale/timezone
   - Write the image

3. **First Boot**
   - Insert SD card into Raspberry Pi
   - Connect to network (Ethernet or WiFi configured above)
   - Power on and wait 1-2 minutes for boot
   
4. **Connect from Windows**
   ```powershell
   # Find your Pi's IP (check router or try):
   ping raspberrypi.local
   
   # SSH into the Pi:
   ssh pi@raspberrypi.local
   # or
   ssh pi@<IP_ADDRESS>
   ```
   
   **All remaining steps run on the Raspberry Pi via SSH or direct terminal.**

## Step 2: Initial Setup

1. **Boot the Raspberry Pi**
   - Insert SD card
   - Connect display via HDMI
   - Connect keyboard/mouse (for initial setup)
   - Power on

2. **Login**
   - Username: `pi`
   - Password: (what you set in imager)

3. **Update System**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

4. **Configure System**
   ```bash
   sudo raspi-config
   ```
   - System Options → Boot / Auto Login → Console Autologin
   - Display Options → Resolution (set appropriate for your display)
   - Localisation Options → Configure timezone, keyboard, WiFi country
   - Advanced Options → Expand Filesystem
   - Finish and reboot

## Step 3: Install SnackAttack

1. **Clone the Repository**
   ```bash
   cd /home/pi
   git clone https://github.com/DouglasHalse/snackAttackTrack.git
   cd snackAttackTrack
   ```

2. **Run Auto-start Setup Script**
   ```bash
   chmod +x rpi-setup/setup-autostart.sh
   ./rpi-setup/setup-autostart.sh
   ```

3. **Configure Database and Settings**
   ```bash
   cd GuiApp
   # Set up your initial database, admin users, etc.
   # Copy your settings file if you have one
   ```

## Step 4: Test Auto-start

1. **Reboot**
   ```bash
   sudo reboot
   ```

2. **Verify**
   - The Pi should boot directly to SnackAttack GUI
   - No desktop environment should load
   - Cursor should hide after 5 seconds of inactivity

## Step 5: Create Custom Image (Optional)

Once everything is working, you can create a reusable image:

1. **Shutdown the Pi**
   ```bash
   sudo shutdown -h now
   ```

2. **Remove SD Card and Insert into Computer**

3. **Create Image Backup**

   **On Linux/macOS:**
   ```bash
   # Find the SD card device (e.g., /dev/sdb or /dev/disk2)
   lsblk  # or diskutil list on macOS
   
   # Create image
   sudo dd if=/dev/sdX of=snackattack-rpi.img bs=4M status=progress
   
   # Compress image
   gzip snackattack-rpi.img
   ```

   **On Windows:**
   - Use Win32DiskImager or similar tool
   - Read from SD card to .img file
   - Compress with 7-Zip

4. **Shrink Image (Optional)**
   - Use PiShrink on Linux to reduce image size:
   ```bash
   wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
   chmod +x pishrink.sh
   sudo ./pishrink.sh snackattack-rpi.img
   ```

## Deployment

To deploy this image to new Raspberry Pis:

1. Flash the custom image to SD card using Raspberry Pi Imager or dd
2. Boot the Pi
3. Update WiFi credentials if needed (edit `/etc/wpa_supplicant/wpa_supplicant.conf`)
4. Optionally update the application: `~/update-snackattack.sh`

## Customization

### Change Display Resolution

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add/uncomment these lines:
```
hdmi_force_hotplug=1
hdmi_drive=2
hdmi_group=2
hdmi_mode=82  # 1920x1080 60Hz, change as needed
```

Common hdmi_mode values:
- 4: 1280x720 60Hz
- 16: 1024x768 60Hz
- 82: 1920x1080 60Hz
- 85: 1280x720 60Hz

### Add Touchscreen Support

If using official RPi touchscreen:
```bash
sudo apt-get install -y python3-evdev
```

For other touchscreens, install appropriate drivers.

### Performance Tuning

Edit `/boot/config.txt`:
```
# Overclock (use with caution, needs good cooling)
arm_freq=1750
gpu_freq=600

# Allocate more GPU memory
gpu_mem=256
```

### Remote Access

**SSH** is already enabled. Connect via:
```bash
ssh pi@<raspberry-pi-ip>
```

**VNC** for remote desktop (optional):
```bash
sudo apt-get install -y realvnc-vnc-server
sudo raspi-config
# Interface Options → VNC → Enable
```

## Troubleshooting

### Application Doesn't Start
```bash
# Check logs
journalctl -xe

# Test manual start
cd /home/pi/snackAttackTrack/GuiApp
python3 main.py
```

### Display Issues
```bash
# Edit boot config
sudo nano /boot/config.txt

# Force HDMI
hdmi_force_hotplug=1
```

### Touch Input Not Working
```bash
# Check input devices
ls /dev/input/

# Install evtest to debug
sudo apt-get install evtest
sudo evtest
```

### App Crashes/Needs Restart
```bash
# Use helper script
~/restart-snackattack.sh

# Or manually
sudo systemctl restart display-manager
```

## Maintenance

### Update Application
```bash
~/update-snackattack.sh
```

### Manual Update
```bash
cd /home/pi/snackAttackTrack
git pull
pip3 install -r requirements-raspberry-pi.txt
~/restart-snackattack.sh
```

### View Logs
```bash
# System logs
journalctl -u getty@tty1 -f

# Application logs (if logging to file)
tail -f /home/pi/snackAttackTrack/GuiApp/*.log
```

### Backup Database
```bash
# Copy database file
cp /home/pi/snackAttackTrack/GuiApp/SnackAttackDatabase.db ~/backup-$(date +%Y%m%d).db

# Or use automated backup script
# (Create one in crontab)
```

## Security Considerations

1. **Change Default Password**
   ```bash
   passwd
   ```

2. **Update Regularly**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

3. **Firewall (Optional)**
   ```bash
   sudo apt-get install ufw
   sudo ufw allow ssh
   sudo ufw enable
   ```

4. **Disable SSH if Not Needed**
   ```bash
   sudo systemctl disable ssh
   sudo systemctl stop ssh
   ```

## Additional Resources

- Raspberry Pi Documentation: https://www.raspberrypi.com/documentation/
- Kivy on Raspberry Pi: https://kivy.org/doc/stable/installation/installation-rpi.html
- PiShrink: https://github.com/Drewsif/PiShrink
