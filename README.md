# E-ink Server Monitor

A real-time server monitoring display using a 2.13" Waveshare E-ink display and Prometheus metrics. Perfect for at-a-glance monitoring of your server's vital statistics including UPS status, GPU metrics, CPU performance, and system resources.


## Features

- **Three-column layout** optimized for 2.13" (250x122) E-ink displays
- **Real-time metrics** from Prometheus
- **UPS monitoring**: Battery level, runtime, load, temperature, voltage
- **GPU monitoring**: Temperature, utilization, power draw, fan speed, clock speeds
- **System monitoring**: CPU temperature/frequency/usage, memory, disk usage, chassis fan
- **Partial refresh support** to minimize screen flicker
- **Low power consumption** perfect for 24/7 operation

## Hardware Requirements

- Raspberry Pi (any model with GPIO support)
- Waveshare 2.13" E-ink Display V4 (250x122 resolution)
- Server running Prometheus with appropriate exporters

## Software Requirements

### On the Raspberry Pi (Display Device)

- Python 3.7 or higher
- Waveshare E-paper library
- Required Python packages:
  - `requests`
  - `Pillow` (PIL)
  - SPI interface enabled

### On Your Server (Being Monitored)

**Prometheus does NOT need to be installed on the Raspberry Pi.** Prometheus should be running on the server you want to monitor (or a dedicated monitoring server). The Raspberry Pi only needs network access to query the Prometheus API.

Required Prometheus exporters on your server:
- **Node Exporter** - For CPU, memory, disk, and fan metrics
- **NVIDIA GPU Exporter** - For GPU metrics (if monitoring NVIDIA GPU)
- **Custom UPS Exporter** - For UPS metrics (or SNMP exporter for UPS)

## Installation

### 1. Prepare the Raspberry Pi

Enable SPI interface:
```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
```

Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-numpy git
```

### 2. Install Waveshare E-paper Library

```bash
cd ~
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
```

### 3. Clone This Repository

```bash
cd ~
git clone https://github.com/yourusername/eink-server-monitor.git
cd eink-server-monitor
```

### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 5. Configure the Monitor

Edit `monitor.py` and update the configuration section:

```python
# Configuration
PROMETHEUS_URL = "http://192.168.100.55:9090"  # Change to your Prometheus server IP
REFRESH_INTERVAL = 20  # Seconds between updates
FULL_REFRESH_CYCLES = 10  # Full refresh every N partial refreshes
```

**Important:** Update the server name and GPU model in the code:
- **Line 79**: Change `'DELL 7820 Server Stats'` to your server name
- **Line 142**: Change `'RTX 3090 Ti'` to your actual GPU model name

### 6. Set Up Prometheus Exporters on Your Server

This project expects specific Prometheus metrics. Ensure your server has:

**Node Exporter:**
```bash
# Download and run Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz
cd node_exporter-1.7.0.linux-amd64
./node_exporter
```

**NVIDIA GPU Exporter:**
```bash
# Install nvidia_gpu_prometheus_exporter
pip install nvidia-gpu-prometheus-exporter
nvidia_gpu_prometheus_exporter
```

**UPS Exporter:**
Set up an SNMP exporter or custom exporter for your UPS that exposes the following metrics:
- `ups_battery_charge_percent`
- `ups_runtime_minutes`
- `ups_load_percent`
- `ups_temperature_celsius`
- `ups_input_voltage`
- `ups_output_voltage`
- `ups_load_current`

## Usage

### Manual Run

```bash
python3 monitor.py
```

Press `Ctrl+C` to stop the monitor gracefully.

### Run as Systemd Service (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/eink-monitor.service
```

Add the following content:

```ini
[Unit]
Description=E-ink Server Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/eink-server-monitor
ExecStart=/usr/bin/python3 /home/pi/eink-server-monitor/monitor.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable eink-monitor.service
sudo systemctl start eink-monitor.service
```

Check status:
```bash
sudo systemctl status eink-monitor.service
```

View logs:
```bash
journalctl -u eink-monitor.service -f
```

## Customization

### Changing Displayed Metrics

The monitor queries Prometheus with specific query strings. To modify what's displayed, edit the `query_prometheus()` calls in the `draw_display()` method.

Example - changing CPU temperature sensor:
```python
# Original
cpu_temp = self.query_prometheus('node_hwmon_temp_celsius{chip="platform_coretemp_0",sensor="temp1"}')

# Modified for different sensor
cpu_temp = self.query_prometheus('node_hwmon_temp_celsius{chip="k10temp",sensor="temp1"}')
```

### Adjusting Layout

Modify these variables in `draw_display()`:
- `col1_x`, `col2_x`, `col3_x` - Column x-positions
- `start_y` - Starting y-position for content
- Font sizes and spacing in the y-increment values

### Changing Refresh Interval

Adjust these constants:
```python
REFRESH_INTERVAL = 20  # Seconds between updates
FULL_REFRESH_CYCLES = 10  # Full refresh every 200 seconds (20s * 10)
```

## Troubleshooting

### Display not working
- Verify SPI is enabled: `lsmod | grep spi`
- Check wiring connections
- Ensure Waveshare library is installed correctly

### No metrics showing
- Verify Prometheus URL is accessible: `curl http://your-prometheus-ip:9090/api/v1/query?query=up`
- Check that exporters are running on your server
- Verify firewall allows access to Prometheus port 9090

### Font errors
The script will fall back to default fonts if TrueType fonts aren't found. To use better fonts:
```bash
sudo apt-get install fonts-dejavu-core
```

## Display Layout

```
┌────────────────────────────────────────────────┐
│ DELL 7820 Server Stats          HH:MM Mon DD   │
├────────────────────────────────────────────────┤
│ UPS 1500X     │ RTX 3090 Ti   │ CPU            │
│ Battery: XX%  │ Temp: XXC     │ Temp: XXC      │
│ Runtime: XXm  │ Utilization:  │ Freq: X.XGHz   │
│ Load: XX%     │ Power: XXXW   │ Usage: XX%     │
│ Temp: XXC     │ Fan: XX%      │ Mem: XXXG      │
│ Input: XXXV   │ Core: XXXX    │ Disk: X.XT     │
│ Output: XXXV  │ Mem: XXXX     │ Cha.: XXXXrpm  │
└────────────────────────────────────────────────┘
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Waveshare for the excellent E-paper displays and libraries
- Prometheus project for the powerful monitoring system
- The open-source community for various exporters

## Support

If you find this project helpful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=bcdproduction&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bcdproduction)

## Author

Created for monitoring high-performance servers and GPU workstations with at-a-glance real-time statistics.
