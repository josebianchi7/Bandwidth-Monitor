# Description: Program to listen for GET requests and respond
#   with data from local log file.

import json
from flask import Flask, jsonify
from credentials import host_ip
from credentials import host_port


# Flask app to serve data usage reports
app = Flask(__name__)

# Path to the log file
log_file = 'usage_log.txt'

# Function to read the log file and return entries for the current day
def get_log_data_for_today():
    day_count = 0
    log_data = []
    
    try:
        # Open the log file and read the contents
        with open(log_file, 'r') as file:
            lines = file.readlines()
        
            # Filter the log data for the current date
            for line in lines:
                if line[0] == '#':
                    day_count += 1
                if day_count >= 2:
                    break
                log_data.append(line)

    except Exception as e:
        print(f"Error reading log file: {e}")
    log_data.pop(0)

    return log_data

# Define the route for the client to request the log data
@app.route('/usage_report', methods=['GET'])
def get_log_data():
    log_data = get_log_data_for_today()

    if log_data:
        return jsonify(log_data), 200
    else:
        return jsonify({"error": "No log data found for today."}), 404

if __name__ == "__main__":
    # Start the Flask web server
    app.run(host=host_ip, port=host_port)
