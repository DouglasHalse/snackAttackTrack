# Testing SnackAttack with VMware

You can test the Raspberry Pi setup using VMware before deploying to actual hardware. This guide covers testing on VMware Workstation Player (Windows) or VMware Fusion (macOS).

## Prerequisites

### VMware Software
- **Windows:** [VMware Workstation Player](https://www.vmware.com/products/workstation-player.html) (Free for personal use)
- **macOS:** [VMware Fusion Player](https://www.vmware.com/products/fusion.html) (Free for personal use)
- **Alternative:** [VirtualBox](https://www.virtualbox.org/) (Free, cross-platform)

### System Requirements
- 4GB+ RAM (allocate 2GB to VM)
- 20GB+ free disk space
- CPU with virtualization support (VT-x/AMD-V enabled in BIOS)

## Option 1: Test with Standard Debian/Ubuntu (Recommended)

Since Raspberry Pi OS is based on Debian, you can test with standard x86/x64 Debian/Ubuntu:

### Download OS Image
- **Debian:** https://www.debian.org/distrib/netinst (choose AMD64 netinst)
- **Ubuntu Server:** https://ubuntu.com/download/server (minimal installation)
- **Xubuntu:** https://xubuntu.org/download/ (if you want desktop for easier testing)

### VMware Setup

1. **Create New Virtual Machine**
   - Open VMware Workstation/Fusion
   - File → New Virtual Machine
   - Select "Installer disc image file (iso)" → Browse to downloaded ISO
   - Guest OS: Linux → Debian 11.x 64-bit (or Ubuntu 64-bit)
   
2. **Configure VM Resources**
   - Name: SnackAttack-Test
   - Location: Choose storage location
   - Disk size: 20GB (single file is fine)
   - Memory: 2048MB (2GB)
   - Processors: 2
   - Network: NAT (for internet access)
   - Display: Use host settings for monitors
   
3. **Customize Hardware (Optional)**
   - Display → Accelerate 3D graphics: ✓ Enable
   - Display → Graphics memory: 512MB or higher
   
4. **Install OS**
   - Start VM and follow installation:
   - Username: `pi` (to match Raspberry Pi)
   - Password: Your choice
   - For Ubuntu/Debian: Choose **minimal installation** or **basic server**
   - Partitioning: Use entire disk (automatic)
   
5. **First Boot Setup**
   ```bash
   # Update system
   sudo apt-get update
   sudo apt-get upgrade -y
   
   # Install basic tools
   sudo apt-get install -y git curl wget
   ```

### Run SnackAttack Setup

```bash
# Clone repository
cd ~
git clone https://github.com/DouglasHalse/snackAttackTrack.git
cd snackAttackTrack/rpi-setup

# Run quick deploy script
chmod +x quick-deploy.sh
./quick-deploy.sh

# Reboot to test auto-start
sudo reboot
```

After reboot, SnackAttack should automatically launch in fullscreen.

## Option 2: Test with Raspberry Pi OS (ARM Emulation)

You can actually run Raspberry Pi OS in VMware using QEMU emulation, though it's slower:

### Download Raspberry Pi OS
- Go to https://www.raspberrypi.com/software/operating-systems/
- Download "Raspberry Pi OS with desktop" (not Lite, for easier testing in VM)
- Extract the .img file from the .zip

### Convert Image for VMware

**On Windows (using WSL or Git Bash):**
```bash
# Install qemu-img (in WSL)
sudo apt-get install qemu-utils

# Convert img to vmdk
qemu-img convert -f raw -O vmdk 2024-XX-XX-raspios-bullseye-armhf.img raspi-test.vmdk
```

**On macOS:**
```bash
# Install qemu
brew install qemu

# Convert
qemu-img convert -f raw -O vmdk 2024-XX-XX-raspios-bullseye-armhf.img raspi-test.vmdk
```

### Create VM
1. Create new VM → I will install the operating system later
2. Guest OS: Other → Other (32-bit) or Debian ARM
3. Use converted VMDK as existing disk
4. Configure similar to Option 1

**Note:** ARM emulation is very slow. Option 1 (x86 Debian/Ubuntu) is faster for testing.

## Option 3: VirtualBox (Alternative)

VirtualBox is free and works well for testing:

### Setup VirtualBox VM

1. **Download & Install VirtualBox**
   - https://www.virtualbox.org/wiki/Downloads
   - Install VirtualBox Extension Pack for better USB/display support

2. **Create New VM**
   - Name: SnackAttack-Test
   - Type: Linux
   - Version: Debian (64-bit) or Ubuntu (64-bit)
   - Memory: 2048MB
   - Create virtual hard disk: 20GB VDI
   
3. **Configure Settings**
   - System → Motherboard → Boot Order: Optical, Hard Disk
   - System → Processor → 2 CPUs
   - Display → Video Memory: 128MB
   - Display → Graphics Controller: VMSVGA
   - Display → Enable 3D Acceleration: ✓
   - Network → Adapter 1: NAT
   
4. **Install OS**
   - Storage → Controller IDE → Empty → Choose disk image (Debian/Ubuntu ISO)
   - Start VM and install OS
   - Create user `pi` for consistency

5. **Install Guest Additions** (for better performance)
   ```bash
   sudo apt-get install -y build-essential dkms linux-headers-$(uname -r)
   # Devices → Insert Guest Additions CD image
   sudo mount /dev/cdrom /mnt
   sudo /mnt/VBoxLinuxAdditions.run
   sudo reboot
   ```

## Testing the Setup

### 1. Basic Functionality Test

After auto-start is configured:

```bash
# Check if app starts automatically after login
# You should see SnackAttack GUI launch

# Test manual start
cd ~/snackAttackTrack/GuiApp
python3 main.py
```

### 2. Test Helper Scripts

```bash
# Restart app
~/restart-snackattack.sh

# Update app
~/update-snackattack.sh

# Stop app
~/stop-snackattack.sh
```

### 3. Test Database Operations

1. Create admin user
2. Add test snacks
3. Create regular users
4. Test purchases
5. Test top-ups
6. Check transaction history

### 4. Performance Check

```bash
# Run performance test
~/test-performance.sh

# Check resource usage
htop  # Install with: sudo apt-get install htop
```

### 5. Test Auto-Logout

- Login as regular user
- Leave idle for configured timeout
- Verify auto-logout works

## Simulating Raspberry Pi Hardware

### Touchscreen Simulation

VMware/VirtualBox mouse clicks work like touch events in Kivy, so basic testing works. For advanced touch testing:

1. **Enable tablet mode** in VM settings (VirtualBox: System → Pointing Device → USB Tablet)
2. **Use touch monitor** if you have one connected to host

### RFID Reader Simulation

Since you won't have actual RFID hardware in VM:

```bash
# Option 1: Use keyboard input instead
# The app should fall back to manual user selection

# Option 2: Simulate USB device passthrough
# In VMware: VM → Removable Devices → USB device
# Then use a USB RFID reader on host machine
```

For testing without RFID:
- Use the "Create New User" button
- Test login by selecting users from list
- Guest mode testing

## Differences from Real Raspberry Pi

### What Works Differently:

❌ **Won't work in VM:**
- GPIO pins (for additional hardware)
- Exact boot timing (VMs boot differently)
- Hardware-specific drivers
- Some OpenGL features (depending on VM graphics)

✓ **Works the same:**
- Python application logic
- Database operations
- UI/UX and screen layouts
- Auto-start mechanism
- All app features (purchases, top-ups, gamble, etc.)
- User management
- Transaction processing

### Performance Notes:

- VM will be **slower** than real Raspberry Pi for some operations
- VM will be **faster** for database and Python operations (if host is powerful)
- Graphics may have different performance characteristics

## Recommended Testing Workflow

1. **Test in VM first** - Debug application logic, UI, workflows
2. **Fix issues** - Easier to take snapshots, test changes
3. **Create VM snapshot** - Before making changes
4. **Test auto-start** - Verify boot sequence works
5. **Deploy to real Pi** - Final testing on actual hardware
6. **Create custom image** - Once everything works

## VMware Snapshot Strategy

Before major changes:

```
VM → Snapshot → Take Snapshot
```

Useful snapshot points:
- "Fresh OS Install"
- "After Dependencies Install"
- "After SnackAttack Setup"
- "After Database Configuration"
- "Production Ready"

## Troubleshooting VM Issues

### Display Resolution Issues

```bash
# In VM terminal
xrandr  # Check available resolutions
xrandr -s 1920x1080  # Set resolution

# Or edit /boot/config.txt equivalent for GRUB
sudo nano /etc/default/grub
# Add: GRUB_GFXMODE=1920x1080
sudo update-grub
```

### Graphics Acceleration

If Kivy complains about OpenGL:

```bash
# Install Mesa drivers
sudo apt-get install -y mesa-utils libgl1-mesa-dri

# Test OpenGL
glxinfo | grep "OpenGL"

# For VMware
sudo apt-get install open-vm-tools open-vm-tools-desktop
```

### Slow Performance

1. Allocate more RAM (4GB if possible)
2. Increase video memory
3. Enable 3D acceleration
4. Use SSD for VM storage
5. Close other applications

### Network Issues

```bash
# Check network
ping google.com

# Reset network
sudo systemctl restart NetworkManager

# Check IP
ip addr show
```

## Exporting VM for Team Testing

After setting up a working VM:

### VMware
1. File → Export to OVF
2. Save as OVF/OVA file
3. Share with team
4. Import: File → Open

### VirtualBox
1. File → Export Appliance
2. Format: OVF 2.0
3. Include manifest
4. Share .ova file
5. Import: File → Import Appliance

## Converting VM to Raspberry Pi Image

Once VM is working, you can use it as a reference for Raspberry Pi:

1. **Document your setup steps** - What you installed, what you configured
2. **Test scripts on clean VM** - Ensure repeatability
3. **Apply same steps to Pi** - Should work identically
4. **Adjust for Pi-specific items** - GPIO, display settings, etc.

## Conclusion

VMware/VirtualBox testing is perfect for:
- ✅ Developing and debugging the application
- ✅ Testing workflows and user interactions
- ✅ Database schema changes
- ✅ UI/UX refinement
- ✅ Training team members
- ✅ Creating demos

But you should still test on real Raspberry Pi for:
- Final performance validation
- Hardware-specific features (RFID, GPIO)
- Display calibration
- Production deployment testing

**Pro tip:** Keep a VM snapshot of your working configuration. If something breaks on the Pi, you can compare with the VM to troubleshoot!
