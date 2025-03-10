import psutil
import time
import json
import requests
import os
from datetime import datetime
from collections import defaultdict
from credentials import url_notify

log_file = 'usage_log.txt'

with open('recorded_devices.json', 'r') as f:
    devices = json.load(f)

# Initialize dictionaries for tracking device usage and connection times
usage_data = defaultdict(lambda: {
    'sent': 0, 
    'received': 0, 
    'start_time': None, 
    'device_name': None, 
    'threshold': None, 
    'max_active_time': None}
    )


def send_alert(device_ip, sent, received, alert_type="Bandwidth", device_name="Unknown"):
    """
    Sends alert messages via HTTP Post request.
    """
    if alert_type == "Bandwidth":
        message = {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "eventDescription": f"Concerning bandwidth usage detected for device, {device_name}, IP: {device_ip}. Sent: {sent}. Received: {received}.",
            "source": "Bandwidth"
        }
    elif alert_type == "Overuse":
        message = {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "eventDescription": f"Overuse detected for device, {device_name}, IP: {device_ip}. Sent: {sent}. Received: {received}.",
            "source": "Bandwidth"
        }
    else:
        message = {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "eventDescription": f"Check bandwidth usage for device, {device_name}, IP: {device_ip}. Sent: {sent}. Received: {received}.",
            "source": "Bandwidth"
        }
    response = requests.post(url_notify, json=message)
    if response.status_code == 200:
        print(f"Event alert sent.")
    else:
        print(f"Failed to send alert for IP: {device_ip}")


def log_usage():
    """
    Logs usage to local file.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_data = {}

   # Check if the log file exists and is not empty
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        try:
            # Open and read the existing log file
            with open(log_file, 'r') as f:
                lines = f.readlines()

            for line in lines:
                if line.strip():  # Avoid empty lines
                    try:
                        # Try to parse each line as JSON
                        device_data = json.loads(line.strip())
                        # If the line is for the current day, update the data
                        if current_date in device_data.get('date', ''):
                            ip = device_data['ip']
                            current_data[ip] = device_data
                    except json.JSONDecodeError:
                        print("updating log file for current day")
        except Exception as e:
            print(f"Error reading log file: {e}")

    # Update current data with the latest usage information
    for ip, data in usage_data.items():
        if data['sent'] > 0 or data['received'] > 0:  # Only include devices that have used bandwidth
            # Check if the device already has an entry for the current day
            if ip in current_data:
                # Update existing entry (combine sent and received, and update active time)
                current_data[ip]['usage'] += ((data['sent'] + data['received']) / (10**9))
                current_data[ip]['sent'] += data['sent']
                current_data[ip]['received'] += data['received']
                current_data[ip]['active_time'] = (datetime.now() - current_data[ip]['start_time']).total_seconds()
            else:
                # Create a new entry for a device with no existing log entry
                current_data[ip] = {
                    'ip': ip,
                    'device_name': data['device_name'],
                    'sent': data['sent'],
                    'received': data['received'],
                    'usage': (data['sent'] + data['received']) / (10**9),
                    'active_time': (datetime.now() - data['start_time']).total_seconds(),
                    'threshold': data['threshold'],
                    'max_active_time': (data['max_active_time'])
                }

    if os.path.exists(log_file) is False or os.path.getsize(log_file) == 0:
        # If no log file exists or it's empty, begin the current day's data
        with open(log_file, 'w') as f:
            f.write(f"# Device Usage Log for {current_date}\n")
            for device_data in current_data.values():
                f.write(json.dumps(device_data) + "\n")
    else:
        with open(log_file, 'w') as f:
            f.write(f"# Device Usage Log for {current_date}\n")
            for device_data in current_data.values():
                f.write(json.dumps(device_data) + "\n")


def monitor_bandwidth():
    """
    Monitors bandwidth using psutil library.
    """
    global usage_data
    # Get initial network statistics
    initial_stats = psutil.net_io_counters(pernic=True)
    
    while True:
        time.sleep(60)
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
                        if ip in devices:
                            device_name = devices[ip]['name']
                            bandwidth_threshold = devices[ip]['bandwidth_threshold']
                            max_active_time = devices[ip]['max_active_time']
                        else:
                            # If the device is unknown, use default values
                            device_name = "Unknown Device"
                            bandwidth_threshold = (5 * (10**9))     # 5GB
                            max_active_time = (5 *60 * 60)          # 5hrs
                        
                        if device_name == "Home RouterP" or device_name == "localhost":
                            continue

                        # Track start time if it's the first time seeing this device
                        if usage_data[ip]['start_time'] is None:
                            usage_data[ip]['start_time'] = datetime.now()
                            usage_data[ip]['device_name'] = device_name
                            usage_data[ip]['threshold'] = bandwidth_threshold
                            usage_data[ip]['max_active_time'] = max_active_time
                        
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
                            send_alert(ip, usage_data[ip]['sent'], usage_data[ip]['received'], alert_type="Overuse", device_name=device_name)

        # Update initial stats for the next iteration
        initial_stats = current_stats
        log_usage()

if __name__ == "__main__":
    monitor_bandwidth()
