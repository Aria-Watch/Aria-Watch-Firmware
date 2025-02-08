import time, network, config
from Functions.ErrorHandling import LogMaster

class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.max_attempts = 3
        self.retry_delay = 5  # delay in seconds

    def connect(self):
        if self.wlan.isconnected():
            return True

        try:
            self.wlan.connect(config.WIFI, config.WIFI_PASS)
            time.sleep(2)  # Wait for connection to establish

            for attempt in range(self.max_attempts):
                if self.wlan.isconnected():
                    LogMaster(f"WIFI connected! config: {self.wlan.ifconfig()}", "WIFI", 0)
                    return True
                
                if attempt < self.max_attempts - 1:  # Don't delay after last attempt
                    time.sleep(self.retry_delay)
            
            LogMaster("Failed to connect to WIFI after 3 attempts", "WIFI", 0)
            return False

        except OSError as e:
            LogMaster(f"Failed to connect to WIFI! Error: {str(e)}", "WIFI", 0)
            return False

    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()

_wifi_manager = WiFiManager()
ConnectWifi = _wifi_manager.connect
DisconnectWifi = _wifi_manager.disconnect