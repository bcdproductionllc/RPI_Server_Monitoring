# E-ink Server Monitor 📊

A real-time system monitoring dashboard for Waveshare 2.13" e-ink displays (250x122), displaying server statistics in a clean three-column layout.

**Created by BCD PRODUCTION LLC**

![Display Layout](docs/display-preview.png)

---

## Support This Project ☕

If you find this project helpful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=bcdproduction&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bcdproduction)

---

## Features

- **UPS Monitoring**: Battery level, runtime, load, temperature, voltage, and current
- **GPU Statistics**: Temperature, utilization, power draw, fan speed, and clock speeds (RTX 3090 Ti)
- **System Metrics**: CPU temperature/frequency/usage, memory usage, disk usage, and chassis fan RPM
- **Efficient Updates**: Partial refresh every 20 seconds with full refresh every 10 cycles to minimize ghosting
- **Three-Column Layout**: Organized display optimized for e-ink readability

## Hardware Requirements

- Raspberry Pi (tested on Pi 3/4/5) or similar single-board computer
- Waveshare 2.13" e-ink display V4 (250x122 resolution)
- SPI interface enabled on your Pi

## Software Architecture

This project uses **Prometheus** as the metrics collection backend. You'll need:

1. **Prometheus server** - Can run on the same Raspberry Pi or on a separate server
2. **Exporters** running on the target server(s) you want to monitor:
   - `node_exporter` - System metrics (CPU, memory, disk)
   - `nvidia_gpu_exporter` - GPU metrics
   - Custom UPS exporter (SNMP-based or similar)

**Note**: The Raspberry Pi running the display **does not** need to run Prometheus or exporters itself - it only queries a Prometheus server elsewhere on your network.

## Installation

### 1. Set Up the Display Hardware

Connect your Waveshare 2.13" e-ink display to your Raspberry Pi via the SPI interface.

### 2. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interfacing Options -> SPI -> Enable
```

### 3. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy git
```

### 4. Install Waveshare E-Paper Library

```bash
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
```

### 5. Install Python Dependencies

```bash
pip3 install requests pillow
```

### 6. Clone This Repository

```bash
git clone https://github.com/bcdproductionllc/RPI_Server_Monitoring.git
cd RPI_Server_Monitoring
```

### 7. Copy Waveshare Library Files

Copy the `lib` folder from the Waveshare e-Paper library to your project directory:

```bash
cp -r /path/to/e-Paper/RaspberryPi_JetsonNano/python/lib ./
```

## Configuration

Edit `monitor.py` to configure your setup:

```python
# Prometheus server URL (update to your Prometheus instance)
PROMETHEUS_URL = "http://192.168.100.55:9090"

# Update interval in seconds
REFRESH_INTERVAL = 20

# Full refresh every N cycles (reduces ghosting)
FULL_REFRESH_CYCLES = 10
```

### Prometheus Queries

The monitor queries the following metrics. Adjust the queries in the code to match your exporter labels:

**UPS Metrics:**
- `ups_battery_charge_percent`
- `ups_runtime_minutes`
- `ups_load_percent`
- `ups_temperature_celsius`
- `ups_input_voltage`
- `ups_output_voltage`
- `ups_battery_v`
- `ups_load_current`

**GPU Metrics:**
- `nvidia_gpu_temperature_celsius`
- `nvidia_gpu_utilization_percent`
- `nvidia_gpu_power_draw_watts`
- `nvidia_gpu_fan_percent`
- `nvidia_gpu_clock_graphics_mhz`
- `nvidia_gpu_clock_memory_mhz`

**System Metrics:**
- `node_hwmon_temp_celsius{chip="platform_coretemp_0"}`
- `node_cpu_scaling_frequency_hertz`
- `node_cpu_seconds_total`
- `node_memory_MemTotal_bytes`
- `node_memory_MemAvailable_bytes`
- `node_filesystem_size_bytes{mountpoint="/"}`
- `node_filesystem_avail_bytes{mountpoint="/"}`
- `node_hwmon_fan_rpm{sensor="fan3"}`

## Setting Up Prometheus (On Your Server)

### Install Prometheus

On the server you want to monitor:

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*/
```

### Install Exporters

**Node Exporter** (system metrics):
```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
cd node_exporter-*/
./node_exporter &
```

**NVIDIA GPU Exporter**:
```bash
# Install nvidia_gpu_prometheus_exporter or similar
pip install nvidia-ml-py3
# Use a custom exporter script or an existing one from GitHub
```

### Configure Prometheus

Edit `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'nvidia_gpu'
    static_configs:
      - targets: ['localhost:9835']
  
  - job_name: 'ups'
    static_configs:
      - targets: ['localhost:9614']
```

Start Prometheus:
```bash
./prometheus --config.file=prometheus.yml
```

## Running the Monitor

### Manual Run

```bash
python3 monitor.py
```

### Run as Systemd Service

Create `/etc/systemd/system/eink-monitor.service`:

```ini
[Unit]
Description=E-ink Server Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RPI_Server_Monitoring
ExecStart=/usr/bin/python3 /home/pi/RPI_Server_Monitoring/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable eink-monitor
sudo systemctl start eink-monitor
```

Check status:
```bash
sudo systemctl status eink-monitor
```

## Customization

### Modify Layout

The display uses a three-column layout with dimensions 250x122 pixels. You can adjust column positions and metrics in the `draw_display()` method.

### Change Fonts

Update font paths in the `__init__` method:

```python
self.font_header = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 9)
self.font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 8)
self.font_normal = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 7)
```

### Add More Metrics

Add new Prometheus queries and display them in any column:

```python
new_metric = self.query_prometheus('your_metric_name')
if new_metric:
    self.draw.text((col_x, y), f"Label: {float(new_metric):.1f}", font=self.font_normal, fill=0)
    y += 9
```

## Troubleshooting

**Display not working:**
- Ensure SPI is enabled: `ls /dev/spidev0.0`
- Check wiring connections
- Verify Waveshare library installation

**No data showing:**
- Test Prometheus connection: `curl http://YOUR_PROMETHEUS:9090/api/v1/query?query=up`
- Verify exporters are running on your server
- Check metric names match your Prometheus configuration

**Ghosting issues:**
- Increase `FULL_REFRESH_CYCLES` value
- Decrease `REFRESH_INTERVAL` for more frequent updates

**Import errors:**
- Ensure `lib` folder is in the same directory as `monitor.py`
- Reinstall Waveshare library

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Waveshare for the excellent e-paper displays and libraries
- Prometheus for the powerful metrics collection system
- The open-source community

## Support

If you encounter issues or have questions:
- Open an issue on [GitHub](https://github.com/bcdproductionllc/RPI_Server_Monitoring/issues)
- Check the Waveshare e-Paper wiki
- Review Prometheus documentation

![IMG_9517](https://github.com/user-attachments/assets/25ee6cf3-fc58-4865-adfe-0a6475806f80)


---

**Made with ❤️ by BCD PRODUCTION LLC**

If you find this project helpful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=bcdproduction&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bcdproduction)
