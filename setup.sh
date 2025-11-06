#!/bin/bash
# E-ink Server Monitor Setup Script
# BCD PRODUCTION LLC
# Run with: bash setup.sh

set -e

echo "=========================================="
echo "E-ink Server Monitor Setup"
echo "BCD PRODUCTION LLC"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if SPI is enabled
if [ ! -e /dev/spidev0.0 ]; then
    echo "❌ SPI is not enabled!"
    echo "Please run: sudo raspi-config"
    echo "Navigate to: Interface Options -> SPI -> Enable"
    exit 1
else
    echo "✅ SPI is enabled"
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy git fonts-dejavu

# Install Python packages
echo ""
echo "Installing Python dependencies..."
pip3 install requests pillow

# Check for Waveshare library
if [ ! -d "lib" ]; then
    echo ""
    echo "❌ Waveshare library not found!"
    echo ""
    echo "Please install it manually:"
    echo "1. git clone https://github.com/waveshare/e-Paper.git"
    echo "2. cd e-Paper/RaspberryPi_JetsonNano/python/"
    echo "3. sudo python3 setup.py install"
    echo "4. cp -r lib /path/to/RPI_Server_Monitoring/"
    echo ""
    read -p "Have you installed the Waveshare library? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Waveshare library found"
fi

# Configure Prometheus URL
echo ""
echo "Configuration:"
read -p "Enter your Prometheus server IP (e.g., 192.168.100.55): " PROM_IP
read -p "Enter Prometheus port [9090]: " PROM_PORT
PROM_PORT=${PROM_PORT:-9090}

# Update monitor.py
if [ -f "monitor.py" ]; then
    sed -i "s|PROMETHEUS_URL = \".*\"|PROMETHEUS_URL = \"http://${PROM_IP}:${PROM_PORT}\"|" monitor.py
    echo "✅ Updated Prometheus URL in monitor.py"
fi

# Test Prometheus connection
echo ""
echo "Testing Prometheus connection..."
if curl -s "http://${PROM_IP}:${PROM_PORT}/api/v1/query?query=up" > /dev/null 2>&1; then
    echo "✅ Prometheus connection successful"
else
    echo "⚠️  Warning: Could not connect to Prometheus"
    echo "Please verify the server is running and accessible"
fi

# Ask about systemd service
echo ""
read -p "Install as systemd service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    INSTALL_DIR=$(pwd)
    sudo cp eink-monitor.service /etc/systemd/system/
    sudo sed -i "s|/home/pi/RPI_Server_Monitoring|${INSTALL_DIR}|g" /etc/systemd/system/eink-monitor.service
    sudo sed -i "s|User=pi|User=${USER}|g" /etc/systemd/system/eink-monitor.service
    sudo systemctl daemon-reload
    sudo systemctl enable eink-monitor
    echo "✅ Service installed"
    echo ""
    read -p "Start the service now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl start eink-monitor
        echo "✅ Service started"
        echo ""
        echo "Check status with: sudo systemctl status eink-monitor"
        echo "View logs with: sudo journalctl -u eink-monitor -f"
    fi
else
    echo ""
    echo "You can run manually with: python3 monitor.py"
fi

echo ""
echo "=========================================="
echo "Setup complete! 🎉"
echo "BCD PRODUCTION LLC"
echo "=========================================="
echo ""
echo "Support this project:"
echo "https://www.buymeacoffee.com/bcdproduction"
echo ""
echo "Useful commands:"
echo "  Start service:   sudo systemctl start eink-monitor"
echo "  Stop service:    sudo systemctl stop eink-monitor"
echo "  Service status:  sudo systemctl status eink-monitor"
echo "  View logs:       sudo journalctl -u eink-monitor -f"
echo "  Manual run:      python3 monitor.py"
echo ""
