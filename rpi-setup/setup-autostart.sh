#!/bin/bash
# SnackAttack RPi Auto-start Setup Script
# This script configures Raspberry Pi OS Lite to automatically launch SnackAttack on boot

set -e

echo "=== SnackAttack RPi Auto-start Setup ==="
echo "This will configure your Raspberry Pi to automatically launch SnackAttack on boot"
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    pkg-config \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-{bad,base,good,ugly} \
    gstreamer1.0-{omx,alsa} \
    libmtdev-dev \
    xclip \
    xsel \
    libjpeg-dev \
    libfreetype6-dev \
    libpng-dev \
    xinit \
    x11-xserver-utils \
    matchbox-window-manager

# Install Python dependencies
echo "Installing Python dependencies..."
cd /home/pi/snackAttackTrack
pip3 install -r requirements-raspberry-pi.txt

# Create autostart directory
mkdir -p /home/pi/.config/autostart

# Create systemd service for auto-login
echo "Configuring auto-login..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
EOF

# Create xinitrc for starting the application
echo "Creating X session configuration..."
tee /home/pi/.xinitrc > /dev/null <<'EOF'
#!/bin/bash
# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor after 5 seconds of inactivity
unclutter -idle 5 &

# Start window manager
matchbox-window-manager -use_titlebar no &

# Launch SnackAttack
cd /home/pi/snackAttackTrack/GuiApp
python3 main.py

# If app exits, restart X
sudo systemctl restart display-manager
EOF

chmod +x /home/pi/.xinitrc

# Create bash profile to auto-start X
echo "Configuring auto-start X server..."
tee -a /home/pi/.bash_profile > /dev/null <<'EOF'

# Auto-start X on login to tty1
if [ -z "$DISPLAY" ] && [ "$XDG_VTNR" -eq 1 ]; then
    startx
fi
EOF

# Install unclutter for hiding cursor
echo "Installing cursor hiding utility..."
sudo apt-get install -y unclutter

# Configure boot options
echo "Configuring boot options..."
sudo tee -a /boot/config.txt > /dev/null <<'EOF'

# SnackAttack Display Configuration
# Uncomment and adjust based on your display
# hdmi_force_hotplug=1
# hdmi_drive=2
# hdmi_group=2
# hdmi_mode=82
disable_overscan=1
EOF

# Set up log rotation for the app
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/snackattack > /dev/null <<'EOF'
/home/pi/snackAttackTrack/GuiApp/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 pi pi
}
EOF

# Create a restart script
echo "Creating helper scripts..."
tee /home/pi/restart-snackattack.sh > /dev/null <<'EOF'
#!/bin/bash
# Restart SnackAttack application
sudo systemctl restart display-manager
EOF
chmod +x /home/pi/restart-snackattack.sh

# Create update script
tee /home/pi/update-snackattack.sh > /dev/null <<'EOF'
#!/bin/bash
# Update SnackAttack application
cd /home/pi/snackAttackTrack
git pull
pip3 install -r requirements-raspberry-pi.txt
sudo systemctl restart display-manager
EOF
chmod +x /home/pi/update-snackattack.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "SnackAttack will now automatically launch on boot!"
echo ""
echo "Helper scripts created:"
echo "  ~/restart-snackattack.sh - Restart the application"
echo "  ~/update-snackattack.sh  - Update and restart the application"
echo ""
echo "Please reboot your Raspberry Pi to start SnackAttack automatically:"
echo "  sudo reboot"
echo ""
