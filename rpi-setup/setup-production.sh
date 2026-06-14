#!/bin/bash
# Advanced Image Creation Script
# Creates a production-ready SnackAttack image with additional optimizations

set -e

echo "=== SnackAttack Production Image Setup ==="
echo ""

# Run base setup first
if [ -f "/home/pi/snackAttackTrack/rpi-setup/quick-deploy.sh" ]; then
    echo "Running base deployment..."
    /home/pi/snackAttackTrack/rpi-setup/quick-deploy.sh
else
    echo "Error: Base deployment script not found!"
    exit 1
fi

echo ""
echo "=== Applying Production Optimizations ==="
echo ""

# Disable unnecessary services for faster boot
echo "→ Disabling unnecessary services..."
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service
sudo systemctl disable triggerhappy.service
sudo systemctl disable avahi-daemon.service
echo "✓ Services disabled"

# Configure swappiness for SD card longevity
echo ""
echo "→ Optimizing swap for SD card..."
sudo bash -c 'echo "vm.swappiness=10" >> /etc/sysctl.conf'
echo "✓ Swap optimized"

# Move tmp and log to RAM
echo ""
echo "→ Configuring tmpfs for logs..."
if ! grep -q "/var/log" /etc/fstab; then
    sudo bash -c 'cat >> /etc/fstab << EOF
tmpfs /tmp tmpfs defaults,noatime,nosuid,size=100m 0 0
tmpfs /var/tmp tmpfs defaults,noatime,nosuid,size=30m 0 0
tmpfs /var/log tmpfs defaults,noatime,nosuid,mode=0755,size=100m 0 0
EOF'
fi
echo "✓ tmpfs configured"

# Create RAM-based cache directory
echo ""
echo "→ Creating RAM cache directory..."
mkdir -p /home/pi/.cache
if ! grep -q "/home/pi/.cache" /etc/fstab; then
    sudo bash -c 'echo "tmpfs /home/pi/.cache tmpfs defaults,noatime,nosuid,size=100m,uid=1000,gid=1000 0 0" >> /etc/fstab'
fi
echo "✓ RAM cache configured"

# Install watchdog for automatic recovery
echo ""
echo "→ Installing watchdog..."
sudo apt-get install -y -qq watchdog
sudo bash -c 'cat > /etc/watchdog.conf << EOF
watchdog-device = /dev/watchdog
max-load-1 = 24
EOF'
sudo systemctl enable watchdog
echo "✓ Watchdog enabled"

# Create startup health check
echo ""
echo "→ Creating health check service..."
sudo bash -c 'cat > /etc/systemd/system/snackattack-healthcheck.service << EOF
[Unit]
Description=SnackAttack Health Check
After=getty@tty1.service

[Service]
Type=oneshot
ExecStart=/home/pi/healthcheck.sh
User=pi

[Install]
WantedBy=multi-user.target
EOF'

cat > /home/pi/healthcheck.sh << 'EOF'
#!/bin/bash
# Health check script
sleep 30  # Wait for app to start
if ! pgrep -f "python3 main.py" > /dev/null; then
    echo "SnackAttack not running! Attempting restart..." | logger
    systemctl restart getty@tty1
fi
EOF
chmod +x /home/pi/healthcheck.sh
sudo systemctl enable snackattack-healthcheck.service
echo "✓ Health check enabled"

# Set up automated backups
echo ""
echo "→ Setting up database backup..."
cat > /home/pi/backup-database.sh << 'EOF'
#!/bin/bash
# Automated database backup
BACKUP_DIR="/home/pi/backups"
DB_PATH="/home/pi/snackAttackTrack/GuiApp/SnackAttackDatabase.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_DIR/snackattack_$DATE.db"
    # Keep only last 7 backups
    cd "$BACKUP_DIR"
    ls -t snackattack_*.db | tail -n +8 | xargs -r rm
    echo "Database backed up: snackattack_$DATE.db"
fi
EOF
chmod +x /home/pi/backup-database.sh

# Add daily backup cron job
(crontab -l 2>/dev/null || true; echo "0 2 * * * /home/pi/backup-database.sh") | crontab -
echo "✓ Automated backups configured"

# Boot optimization - reduce GPU memory on non-graphical tasks
echo ""
echo "→ Optimizing boot configuration..."
sudo bash -c 'cat >> /boot/config.txt << EOF

# Production Optimizations
boot_delay=0
disable_splash=1
avoid_warnings=1

# Audio (disable if not needed)
# dtparam=audio=off

# Reduce GPU memory for kiosk use
gpu_mem=128
EOF'
echo "✓ Boot optimized"

# Configure read-only mode option (commented by default)
echo ""
echo "→ Creating read-only mode script..."
cat > /home/pi/enable-readonly.sh << 'EOF'
#!/bin/bash
# Enable read-only filesystem for SD card longevity
# WARNING: Run this only after all configuration is complete!

echo "This will make the filesystem read-only to protect SD card."
echo "Database and logs will be in RAM (lost on reboot)."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 1
fi

# Make database directory tmpfs
sudo bash -c 'echo "tmpfs /home/pi/snackAttackTrack/GuiApp tmpfs defaults,noatime,size=200m,uid=1000,gid=1000 0 0" >> /etc/fstab'

# Remount root as read-only
sudo sed -i 's/defaults/defaults,ro/' /etc/fstab

echo "Read-only mode will be enabled on next boot."
echo "To make changes, remount with: sudo mount -o remount,rw /"
EOF
chmod +x /home/pi/enable-readonly.sh
echo "✓ Read-only script created (not enabled by default)"

# Create production checklist
echo ""
echo "→ Creating deployment checklist..."
cat > /home/pi/DEPLOYMENT_CHECKLIST.txt << 'EOF'
SnackAttack Production Deployment Checklist
===========================================

Before creating final image:
☐ Change default password (passwd)
☐ Configure WiFi settings
☐ Set up database with initial admin user
☐ Test auto-boot functionality
☐ Verify touchscreen/display calibration
☐ Check RFID reader connectivity
☐ Configure system settings in app
☐ Test purchase workflow
☐ Test top-up workflow
☐ Verify all screens accessible
☐ Check auto-logout timing
☐ Test database backup script
☐ Review logs for errors
☐ Clean up any test data
☐ Set production timezone
☐ Disable SSH (if not needed)
☐ Enable firewall (if networked)

Before shutdown for imaging:
☐ Clear bash history: history -c && history -w
☐ Clear logs: sudo rm /var/log/*.log
☐ Clear temp files: sudo rm -rf /tmp/*
☐ Clear cache: rm -rf ~/.cache/*
☐ Remove sensitive data
☐ Final backup of database

After flashing to new device:
☐ Expand filesystem (raspi-config)
☐ Change hostname (raspi-config)
☐ Update WiFi credentials
☐ Change admin password in app
☐ Verify auto-start works
☐ Test all functionality

Optional hardening:
☐ Enable read-only mode (~/enable-readonly.sh)
☐ Set up VPN for remote access
☐ Configure static IP
☐ Set up remote monitoring
EOF
echo "✓ Checklist created"

# Performance test script
echo ""
echo "→ Creating performance test script..."
cat > /home/pi/test-performance.sh << 'EOF'
#!/bin/bash
# Quick performance test

echo "=== System Performance Test ==="
echo ""
echo "CPU Temperature:"
vcgencmd measure_temp

echo ""
echo "CPU Frequency:"
vcgencmd measure_clock arm

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "GPU Memory:"
vcgencmd get_mem arm
vcgencmd get_mem gpu

echo ""
echo "Throttling Status:"
vcgencmd get_throttled

echo ""
echo "Uptime:"
uptime

echo ""
echo "Boot Time:"
systemd-analyze

echo ""
echo "Active Processes:"
ps aux --sort=-%mem | head -10
EOF
chmod +x /home/pi/test-performance.sh
echo "✓ Performance test script created"

# Final summary
echo ""
echo "=== Production Setup Complete ==="
echo ""
echo "Additional optimizations applied:"
echo "  • Disabled unnecessary services for faster boot"
echo "  • Optimized swap for SD card longevity"
echo "  • Configured tmpfs for logs and cache"
echo "  • Enabled watchdog for automatic recovery"
echo "  • Set up automated database backups"
echo "  • Created deployment checklist"
echo ""
echo "New helper scripts:"
echo "  ~/backup-database.sh      - Manual database backup"
echo "  ~/enable-readonly.sh      - Enable read-only mode (advanced)"
echo "  ~/test-performance.sh     - System performance check"
echo ""
echo "Review the checklist: ~/DEPLOYMENT_CHECKLIST.txt"
echo ""
echo "Ready to reboot and test!"
echo ""
