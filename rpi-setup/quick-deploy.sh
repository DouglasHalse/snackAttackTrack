#!/bin/bash
# Quick Deploy Script for SnackAttack on Fresh Raspberry Pi OS Lite

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   SnackAttack Quick Deploy for RPi    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo -e "${RED}⚠ Warning: This script is designed to run as the 'pi' user${NC}"
    echo -e "${YELLOW}Current user: $USER${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check internet connectivity
echo -e "${YELLOW}→${NC} Checking internet connection..."
if ! ping -c 1 google.com &> /dev/null; then
    echo -e "${RED}✗ No internet connection. Please connect to the internet first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Internet connected"

# Update system
echo ""
echo -e "${YELLOW}→${NC} Updating system (this may take a while)..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
echo -e "${GREEN}✓${NC} System updated"

# Install dependencies
echo ""
echo -e "${YELLOW}→${NC} Installing dependencies..."
sudo apt-get install -y -qq \
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
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-omx \
    gstreamer1.0-alsa \
    libmtdev-dev \
    xclip \
    xsel \
    libjpeg-dev \
    libfreetype6-dev \
    libpng-dev \
    xinit \
    x11-xserver-utils \
    matchbox-window-manager \
    unclutter

echo -e "${GREEN}✓${NC} Dependencies installed"

# Clone or update repository
echo ""
if [ -d "/home/pi/snackAttackTrack" ]; then
    echo -e "${YELLOW}→${NC} SnackAttack directory exists, updating..."
    cd /home/pi/snackAttackTrack
    git pull
else
    echo -e "${YELLOW}→${NC} Cloning SnackAttack repository..."
    cd /home/pi
    git clone https://github.com/DouglasHalse/snackAttackTrack.git
    cd snackAttackTrack
fi
echo -e "${GREEN}✓${NC} Repository ready"

# Install Python dependencies
echo ""
echo -e "${YELLOW}→${NC} Installing Python dependencies..."
pip3 install -q -r requirements-raspberry-pi.txt
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Configure auto-login
echo ""
echo -e "${YELLOW}→${NC} Configuring auto-login..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo bash -c 'cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
EOF'
echo -e "${GREEN}✓${NC} Auto-login configured"

# Create X session config
echo ""
echo -e "${YELLOW}→${NC} Creating X session configuration..."
cat > /home/pi/.xinitrc << 'EOF'
#!/bin/bash
# Disable screen blanking and power management
xset s off
xset -dpms
xset s noblank

# Hide cursor after inactivity
unclutter -idle 5 &

# Start lightweight window manager
matchbox-window-manager -use_titlebar no &

# Launch SnackAttack
cd /home/pi/snackAttackTrack/GuiApp
python3 main.py 2>&1 | tee /home/pi/snackattack.log

# If app exits unexpectedly, wait and restart
sleep 5
startx
EOF
chmod +x /home/pi/.xinitrc
echo -e "${GREEN}✓${NC} X session configured"

# Configure bash to auto-start X
echo ""
echo -e "${YELLOW}→${NC} Configuring auto-start..."
if ! grep -q "startx" /home/pi/.bash_profile 2>/dev/null; then
    cat >> /home/pi/.bash_profile << 'EOF'

# Auto-start X on tty1 login
if [ -z "$DISPLAY" ] && [ "$XDG_VTNR" -eq 1 ]; then
    startx
fi
EOF
fi
echo -e "${GREEN}✓${NC} Auto-start configured"

# Configure display settings
echo ""
echo -e "${YELLOW}→${NC} Configuring display settings..."
if ! grep -q "SnackAttack Display Configuration" /boot/config.txt 2>/dev/null; then
    sudo bash -c 'cat >> /boot/config.txt << EOF

# SnackAttack Display Configuration
disable_overscan=1
# hdmi_force_hotplug=1
# hdmi_drive=2
# hdmi_group=2
# hdmi_mode=82
EOF'
fi
echo -e "${GREEN}✓${NC} Display settings configured"

# Create helper scripts
echo ""
echo -e "${YELLOW}→${NC} Creating helper scripts..."

cat > /home/pi/restart-snackattack.sh << 'EOF'
#!/bin/bash
# Restart SnackAttack
echo "Restarting SnackAttack..."
sudo systemctl restart getty@tty1
EOF
chmod +x /home/pi/restart-snackattack.sh

cat > /home/pi/update-snackattack.sh << 'EOF'
#!/bin/bash
# Update SnackAttack
echo "Updating SnackAttack..."
cd /home/pi/snackAttackTrack
git pull
pip3 install -r requirements-raspberry-pi.txt
echo "Update complete. Restarting..."
sudo systemctl restart getty@tty1
EOF
chmod +x /home/pi/update-snackattack.sh

cat > /home/pi/stop-snackattack.sh << 'EOF'
#!/bin/bash
# Stop SnackAttack and return to console
echo "Stopping SnackAttack..."
killall python3
killall X
EOF
chmod +x /home/pi/stop-snackattack.sh

echo -e "${GREEN}✓${NC} Helper scripts created"

# Set up log rotation
echo ""
echo -e "${YELLOW}→${NC} Setting up log rotation..."
sudo bash -c 'cat > /etc/logrotate.d/snackattack << EOF
/home/pi/snackattack.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    copytruncate
}
EOF'
echo -e "${GREEN}✓${NC} Log rotation configured"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Setup Complete! 🎉            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your database and settings in:"
echo "   /home/pi/snackAttackTrack/GuiApp/"
echo ""
echo "2. Reboot to start SnackAttack automatically:"
echo -e "   ${GREEN}sudo reboot${NC}"
echo ""
echo -e "${YELLOW}Helper scripts created:${NC}"
echo "  ~/restart-snackattack.sh  - Restart the app"
echo "  ~/update-snackattack.sh   - Update and restart"
echo "  ~/stop-snackattack.sh     - Stop the app"
echo ""
echo -e "${YELLOW}Logs location:${NC}"
echo "  ~/snackattack.log"
echo ""
echo -e "${YELLOW}Remote access (if needed):${NC}"
echo "  SSH: ssh pi@$(hostname -I | awk '{print $1}')"
echo ""
