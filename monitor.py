#!/usr/bin/env python3
"""
System Metrics Display for 2.13" E-ink Display (250x122)
Three vertical columns layout
"""

import requests
import time
from datetime import datetime
import sys
import os

# Add the waveshare library path
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont

# Configuration
PROMETHEUS_URL = "http://192.168.100.55:9090"
REFRESH_INTERVAL = 20
FULL_REFRESH_CYCLES = 10

# Display dimensions
DISPLAY_WIDTH = 250
DISPLAY_HEIGHT = 122

class SystemMonitor:
    def __init__(self):
        try:
            self.epd = epd2in13_V4.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            
            self.image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
            self.draw = ImageDraw.Draw(self.image)
            
            try:
                self.font_header = ImageFont.truetype('/usr/share/fonts/truetyp>
                self.font_title = ImageFont.truetype('/usr/share/fonts/truetype>
                self.font_normal = ImageFont.truetype('/usr/share/fonts/truetyp>
            except:
                self.font_header = ImageFont.load_default()
                self.font_title = ImageFont.load_default()
                self.font_normal = ImageFont.load_default()
            
            self.cycle_count = 0
            
        except Exception as e:
            print(f"Error initializing display: {e}")
            sys.exit(1)
    
    def query_prometheus(self, query):
        """Query Prometheus and return the result"""
        try:
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'success' and result['data']['result']:
                return result['data']['result'][0]['value'][1]
            return None
        except Exception as e:
            return None
    
    def draw_display(self):
        """Draw three-column layout"""
        self.draw.rectangle((0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), fill=255)
        
        # Header
        now = datetime.now()
        self.draw.text((2, 1), 'DELL 7820 Server Stats', font=self.font_header,>
        header_text = now.strftime('%H:%M %b %d')
        header_width = self.draw.textlength(header_text, font=self.font_header)
        self.draw.text((DISPLAY_WIDTH - header_width - 2, 1), header_text, font>
        
        # Header separator
        self.draw.line([(0, 11), (DISPLAY_WIDTH, 11)], fill=0, width=1)
        
        # Column widths (roughly equal)
        col1_x = 2
        col2_x = 85
        col3_x = 168
        start_y = 14
        
        # Vertical separators
        self.draw.line([(82, 12), (82, DISPLAY_HEIGHT)], fill=0, width=1)
        self.draw.line([(165, 12), (165, DISPLAY_HEIGHT)], fill=0, width=1)
        
        # COLUMN 1: UPS
        y = start_y
        self.draw.text((col1_x, y), 'UPS 1500X', font=self.font_title, fill=0)
        y += 11
        
        ups_battery = self.query_prometheus('ups_battery_charge_percent')
        ups_runtime = self.query_prometheus('ups_runtime_minutes')
        ups_load = self.query_prometheus('ups_load_percent')
        ups_temp = self.query_prometheus('ups_temperature_celsius')
        ups_input = self.query_prometheus('ups_input_voltage')
        ups_output = self.query_prometheus('ups_output_voltage')
        ups_battery_v = self.query_prometheus('ups_battery_v')
        ups_load_current = self.query_prometheus('ups_load_current')
        
        if ups_battery:
            self.draw.text((col1_x, y), f"Battery: {float(ups_battery):.0f}%", >
            y += 9
        
        if ups_runtime:
            mins = float(ups_runtime)
            self.draw.text((col1_x, y), f"Runtime: {mins:.0f}m", font=self.font>
            y += 9
        
        if ups_load:
            self.draw.text((col1_x, y), f"Load: {float(ups_load):.1f}%", font=s>
            y += 9
        
        if ups_temp:
            self.draw.text((col1_x, y), f"Temp: {float(ups_temp):.0f}C", font=s>
            y += 9
        
        if ups_input:
            self.draw.text((col1_x, y), f"Input: {float(ups_input):.0f}V", font>
            y += 9
        
        if ups_output:
            self.draw.text((col1_x, y), f"Output: {float(ups_output):.0f}V", fo>
            y += 9
       
        if ups_load_current:
            self.draw.text((col1_x, y), f"Load_Amp: {float(ups_load_current):.0>


        # COLUMN 2: GPU
        y = start_y
        self.draw.text((col2_x, y), 'RTX 3090 Ti', font=self.font_title, fill=0)
        y += 11
        
        gpu_temp = self.query_prometheus('nvidia_gpu_temperature_celsius')
        gpu_util = self.query_prometheus('nvidia_gpu_utilization_percent')
        gpu_power = self.query_prometheus('nvidia_gpu_power_draw_watts')
        gpu_fan = self.query_prometheus('nvidia_gpu_fan_percent')
        gpu_clock = self.query_prometheus('nvidia_gpu_clock_graphics_mhz')
        gpu_mem_clock = self.query_prometheus('nvidia_gpu_clock_memory_mhz')
        
        if gpu_temp:
            self.draw.text((col2_x, y), f"Temp: {float(gpu_temp):.0f}°C", font=>
            y += 9
        
        if gpu_util:
            self.draw.text((col2_x, y), f"Utilzation: {float(gpu_util):.0f}%", >
            y += 9
        
        if gpu_power:
            self.draw.text((col2_x, y), f"Power: {float(gpu_power):.0f}W", font>
            y += 9
        
        if gpu_fan:
            self.draw.text((col2_x, y), f"Fan: {float(gpu_fan):.0f}%", font=sel>
            y += 9
        
        if gpu_clock:
            self.draw.text((col2_x, y), f"Core: {float(gpu_clock):.0f}", font=s>
            y += 9
        
        if gpu_mem_clock:
            self.draw.text((col2_x, y), f"Mem: {float(gpu_mem_clock):.0f}", fon>
        
        # COLUMN 3: CPU/System
        y = start_y
        self.draw.text((col3_x, y), 'CPU', font=self.font_title, fill=0)
        y += 11
        
        cpu_temp = self.query_prometheus('node_hwmon_temp_celsius{chip="platfor>
        if cpu_temp is None:
            cpu_temp = self.query_prometheus('avg(node_hwmon_temp_celsius{chip=>
        cpu_freq = self.query_prometheus('avg(node_cpu_scaling_frequency_hertz)>
        cpu_usage = self.query_prometheus('100 - (avg(irate(node_cpu_seconds_to>
        mem_total = self.query_prometheus('node_memory_MemTotal_bytes')
        mem_avail = self.query_prometheus('node_memory_MemAvailable_bytes')
        disk_total = self.query_prometheus('node_filesystem_size_bytes{mountpoi>
        disk_avail = self.query_prometheus('node_filesystem_avail_bytes')
        chasis_fan = self.query_prometheus('node_hwmon_fan_rpm{sensor="fan3"}')
        
        if cpu_temp:
            self.draw.text((col3_x, y), f"Temp: {float(cpu_temp):.0f}°C", font=>
            y += 9
        
        if cpu_freq:
            ghz = float(cpu_freq) / 1000000000
            self.draw.text((col3_x, y), f"Freq: {ghz:.1f}GHz", font=self.font_n>
            y += 9
        
        if cpu_usage:
            self.draw.text((col3_x, y), f"Usage: {float(cpu_usage):.0f}%", font>
            y += 9
        
        if mem_total and mem_avail:
            total_gb = float(mem_total) / (1024**3)
            avail_gb = float(mem_avail) / (1024**3)
            used_gb = total_gb - avail_gb
            self.draw.text((col3_x, y), f"Mem: {used_gb:.0f}G", font=self.font_>
            y += 9
        
        if disk_total and disk_avail:
            total_tb = float(disk_total) / (1024**4)
            avail_tb = float(disk_avail) / (1024**4)
            used_tb = total_tb - avail_tb
            self.draw.text((col3_x, y), f"Disk: {used_tb:.1f}T", font=self.font>
            y += 9

        if chasis_fan:
            self.draw.text((col3_x, y), f"Cha.: {float(chasis_fan):.0f}rpm", fo>
            y += 9

    
    def update_display(self):
        """Update the e-ink display"""
        try:
            self.draw_display()
            
            self.cycle_count += 1
            
            if self.cycle_count >= FULL_REFRESH_CYCLES:
                self.epd.init()
                self.epd.display(self.epd.getbuffer(self.image))
                self.cycle_count = 0
            else:
                self.epd.displayPartial(self.epd.getbuffer(self.image))
            
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def cleanup(self):
        """Clean up display resources"""
        try:
            self.epd.init()
            self.epd.Clear(0xFF)
            self.epd.sleep()
        except:
            pass

def main():
    """Main loop"""
    print("Starting E-ink System Monitor...")
    print(f"Connecting to: {PROMETHEUS_URL}")
    
    monitor = SystemMonitor()
    
    try:
        while True:
            monitor.update_display()
            time.sleep(REFRESH_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        monitor.cleanup()
    
    except Exception as e:
        print(f"Error: {e}")
        monitor.cleanup()

if __name__ == "__main__":
    main()