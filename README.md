# Bandwidth-Monitor

#### Microservice to monitor devices on local network and send an event message if an unusual amount or sudden large increase of bandwidth is being used by a single device.

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

    For Bandwidth monitoring by IP
    ```bash
      $ pip install psutil requests
    ```


2. Create credentials file, credentials.py, and include the following data in string format:
  
    1. url_notify = URL to notify network owner.

3. Create registered_devices.json to include a JSON dictionary of devices and expected thresholds. Example: 
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


## References and Acknowledgements



