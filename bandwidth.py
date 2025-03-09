import psutil
import time
import json
import requests
from datetime import datetime
from collections import defaultdict
from credentials import url_notify

# Load device data from JSON file
with open('registered_devices.json', 'r') as f:
    devices = json.load(f)

# Initialize dictionaries for tracking device usage and connection times
usage_data = defaultdict(lambda: {'sent': 0, 'received': 0, 'start_time': None})

# Function to send HTTP POST request when suspicious usage is detected
def send_alert(device_ip, sent, received, alert_type="Bandwidth"):
    url = url_notify
    name = devices[device_ip]['name']
    message = {
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "eventDescription": f"Suspicious bandwidth usage detected for device, {name}, IP: {device_ip}. Sent: {sent}. Received: {received}."
    }
    response = requests.post(url, json=message)
    if response.status_code == 200:
        print(f"Event alert sent.")
    else:
        print(f"Failed to send alert for IP: {ip}")

# Function to track bandwidth usage
def monitor_bandwidth():
    global usage_data

    # Get initial network statistics
    initial_stats = psutil.net_io_counters(pernic=True)
    
    while True:
        time.sleep(60)  # Monitor every 60 seconds
        
        # Get current stats
        current_stats = psutil.net_io_counters(pernic=True)
        
        for interface, stats in current_stats.items():
            # Calculate the difference in bytes sent and received
            if interface in initial_stats:
                sent_diff = stats.bytes_sent - initial_stats[interface].bytes_sent
                recv_diff = stats.bytes_recv - initial_stats[interface].bytes_recv

                # Iterate over all devices in the network (track via IP)
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED':
                        ip = conn.raddr.ip
                        
                        # Check if the device IP is known (exists in devices.json)
                        if ip in devices:
                            device_name = devices[ip]['name']
                            bandwidth_threshold = devices[ip]['bandwidth_threshold']
                            max_active_time = devices[ip]['max_active_time']
                        else:
                            # If the device is unknown, use default values
                            device_name = "Unknown Device"
                            bandwidth_threshold = devices["unknown"]["bandwidth_threshold"]
                            max_active_time = devices["unknown"]["max_active_time"]

                        # Track start time if it's the first time seeing this device
                        if usage_data[ip]['start_time'] is None:
                            usage_data[ip]['start_time'] = datetime.now()
                        
                        # Update the usage data for the device
                        usage_data[ip]['sent'] += sent_diff
                        usage_data[ip]['received'] += recv_diff

                        # Check for bandwidth threshold exceedance
                        total_usage = usage_data[ip]['sent'] + usage_data[ip]['received']
                        if total_usage > bandwidth_threshold:
                            send_alert(ip, usage_data[ip]['sent'], usage_data[ip]['received'], alert_type="Bandwidth", device_name=device_name)

                        # Check for max active time threshold exceedance
                        current_time = datetime.now()
                        active_duration = (current_time - usage_data[ip]['start_time']).total_seconds()
                        if active_duration > max_active_time:
                            send_alert(ip, usage_data[ip]['sent'], usage_data[ip]['received'], alert_type="Screen Time", device_name=device_name)

        # Update initial stats for the next iteration
        initial_stats = current_stats

if __name__ == "__main__":
    monitor_bandwidth()