# Frequently Asked Questions (FAQ)


## General Questions

### Q: Do I need to install Prometheus on the Raspberry Pi?
**A:** No! The Raspberry Pi only needs to query a Prometheus server running on your network. Prometheus should run on the server you're monitoring or on a dedicated monitoring server.

### Q: What display sizes are supported?
**A:** Currently optimized for Waveshare 2.13" V4 (250x122). Other sizes would require layout modifications.

### Q: How much does this cost?
**A:**
- Waveshare 2.13" e-ink display: ~$15-20
- Raspberry Pi Zero W: ~$15 (or use any Pi you have)
- Total: ~$30-40

### Q: What's the power consumption?
**A:** Very low! The e-ink display only uses power during updates. Between updates it's nearly zero. Total setup uses less than 5W.

### Q: Can I monitor multiple servers?
**A:** Yes, but you'd need to modify the layout. Consider creating multiple displays or rotating between servers.

---

## Technical Questions

### Q: What Prometheus exporters do I need?
**A:**
- **node_exporter** - System metrics (required)
- **nvidia_gpu_exporter** - GPU metrics (if you have NVIDIA GPU)
- **Custom UPS exporter** - UPS metrics (if you have a UPS)

### Q: My metric names are different, what do I do?
**A:** Edit the Prometheus queries in `monitor.py` to match your metric names. Check your Prometheus UI at `http://your-server:9090/graph` to see available metrics.

### Q: Can I use this with InfluxDB or Grafana instead?
**A:** Not directly. The code is designed for Prometheus API. You'd need to modify the `query_prometheus()` method.

### Q: How do I find my metric names?
**A:** Open Prometheus at `http://your-server:9090/graph` and browse available metrics.

### Q: Why use partial refresh?
**A:** Partial refresh is much faster and causes less flicker. Full refresh clears ghosting but takes longer.

---

## Display Questions

### Q: Why is my display showing ghost images?
**A:** Decrease `FULL_REFRESH_CYCLES` from 10 to 5 or 3 for more frequent full refreshes.

### Q: The display updates too slowly
**A:** Decrease `REFRESH_INTERVAL` from 20 seconds to 10 or 15 seconds.

### Q: Can I use a different e-ink display?
**A:** Possibly, but you'll need to:
1. Check if Waveshare provides a Python library
2. Update the import and initialization
3. Adjust display dimensions
4. Modify the layout

### Q: The display is blank after starting
**A:** Check:
- Is SPI enabled? `ls /dev/spidev0.0`
- Are connections secure?
- Check logs: `sudo journalctl -u eink-monitor -n 50`

---

## Installation Questions

### Q: Which Raspberry Pi should I use?
**A:** Any model works:
- **Pi Zero W**: Cheapest, lowest power (recommended)
- **Pi 3/4/5**: If you have one available

### Q: Do I need a GUI/desktop on the Pi?
**A:** No! Raspberry Pi OS Lite (headless) works perfectly.

### Q: Can I run this on other Linux systems?
**A:** Yes, if they support SPI and GPIO. ARM-based systems work best.

### Q: How do I update the code?
**A:**
```bash
cd ~/RPI_Server_Monitoring
git pull
sudo systemctl restart eink-monitor
```

---

## Troubleshooting

### Q: I get "No module named 'waveshare_epd'"
**A:**
1. Ensure you copied the `lib` folder
2. Reinstall: `cd ~/e-Paper/RaspberryPi_JetsonNano/python/ && sudo python3 setup.py install`

### Q: Prometheus queries return None
**A:**
1. Test: `curl http://your-server:9090/api/v1/query?query=up`
2. Check exporters are running
3. Verify metric names

### Q: The service won't start
**A:**
```bash
# Check status
sudo systemctl status eink-monitor

# View logs
sudo journalctl -u eink-monitor -n 50

# Try manual run
cd ~/RPI_Server_Monitoring
python3 monitor.py
```

---

## Customization

### Q: Can I change what metrics are displayed?
**A:** Yes! Edit the `draw_display()` method in `monitor.py`. See CONFIGURATION.md for examples.

### Q: How do I change the layout?
**A:** Modify column positions (`col1_x`, `col2_x`, `col3_x`) in the code.

### Q: Can I change the fonts?
**A:** Yes! Update font paths in the `__init__` method. Available fonts are in `/usr/share/fonts/truetype/`.

### Q: How do I add a fourth column?
**A:** The display is narrow. Options:
1. Reduce font sizes
2. Use a larger display
3. Split metrics into rotating views

---

## Support

### Need More Help?
- Open an issue: https://github.com/bcdproductionllc/RPI_Server_Monitoring/issues
- Check Waveshare e-Paper wiki
- Review Prometheus documentation
- Ask in r/homelab or r/selfhosted

### Support This Project
If you find this helpful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=bcdproduction&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bcdproduction)

---

**BCD PRODUCTION LLC**
