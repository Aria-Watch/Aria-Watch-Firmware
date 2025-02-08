# Main function
from Functions import WifiTools, ReadData, SendData, GPS, Tools, Bluetooth,LedMng
import machine, json
from machine import Pin
import config

def check_BLE():
    button = Pin(3, Pin.OUT)
    button.on()  # PowerOn button
    button_led = Pin(5, Pin.OUT)
    config_button = Pin(4, Pin.IN, Pin.PULL_DOWN)
    
    if config_button.value():
        if config.DEBUG: print("-> START CONFIG MODE")
        button_led.on()
        Bluetooth.StartBLE()
        return
    
    button.off()

def check_daily_tasks(info):
    if info["TodaySamplings"] == 12:
        if config.DEBUG:print("-> It's time to do some cleaning in the logs")
        Tools.LogCleaner()  # Clear log files
        if config.DEVICE_MODEL == "Bora":GPS.readGPSdata()  # One time a day check the GPS

def main():
    LedMng.set_led((111, 218, 235))  

    # BLE and Led management for "Bora"
    if config.DEVICE_MODEL == "Bora":
        check_BLE()
    
    # Read sensor data
    if config.DEBUG: print("-> Start Data Sampling")
    ReadData.ReadData()
    
    # Handle WiFi connection and data sending
    if WifiTools.ConnectWifi():  
        try:
            if config.DEBUG: print("-> Successfully Connect to Wifi, now data will be send to the server")
            SendData.SendData()
        finally:
            if config.DEBUG: print("-> Disconnect from WIFI")
            WifiTools.DisconnectWifi()
    
    # Handle daily tasks
    with open('data/info.json') as f:
        info = json.load(f)
    check_daily_tasks(info)
    
    # Go to sleep
    if config.DEBUG: print("-> Going to sleep! Bye!")
    machine.deepsleep(config.SLEEP_TIME)
    

if __name__ == "__main__":
    main()