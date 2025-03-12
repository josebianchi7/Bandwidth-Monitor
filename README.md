# Bandwidth-Monitor

#### Microservice to monitor devices on local network and send an event message if an unusual amount or sudden large increase of bandwidth is being used by a single device. Program includes additional app.py file to send local log report to main program.

## Authors

- [@josebianchi7](https://github.com/josebianchi7)


## Deployment

To deploy this project, the following is required:

1. Install the following necessary Python libraries (if not already installed):

    For HTTP Post requests with JSON objects
    ```bash
      $ pip install requests
    ```
    ```bash
      $ pip install json
    ```
    ```bash
      $ pip install flask
    ```

    For Bandwidth monitoring by IP
    ```bash
      $ pip install psutil requests
    ```


2. Create credentials file, credentials.py, and include the following data in string format:
  
    1. url_notify = URL to notify network owner.
    
    2. Additionaly, but not required, store IP and Port for Flask app in credentials.py as well.

        host_ip = unused IP on your network

        host_port = 4000

3. Create registered_devices.json to include a JSON dictionary of common IPs and expected thresholds. Example:
   ```
            {
          "unknown": {
            "bandwidth_threshold": 100000000,  # 100MB
            "max_active_time": 10800  # 3 hours
          },
          "192.123.4.5": {
            "name": "Laptop",
            "bandwidth_threshold": 500000000,  # 500MB
            "max_active_time": 18000  # 5 hours
          },
          "192.123.4.6": {
            "name": "Cellphone",
            "bandwidth_threshold": 100000000,  # 100MB
            "max_active_time": 10800  # 3 hours
          },
          "192.123.4.7": {
            "name": "Smart TV",
            "bandwidth_threshold": 2000000000,  # 2GB
            "max_active_time": 14400  # 4 hours
          }
        }

   ```
## References and Acknowledgements

[1] P. D, “Building a Python-based Network Monitoring Tool with Psutil,” peerdh.com, Oct. 2024. https://peerdh.com/blogs/programming-insights/building-a-python-based-network-monitoring-tool-with-psutil (accessed Mar. 08, 2025).

[2] J. Blewitt, “Monitoring Your Bandwidth with Python! 📈,” Joshblewitt.dev, Jan. 02, 2021. https://www.joshblewitt.dev/posts/2021-01-02-python-bandwidth-monitor (accessed Mar. 08, 2025).


