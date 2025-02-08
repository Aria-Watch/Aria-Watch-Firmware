'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

from Functions import WifiTools
from Functions import ReadData
from Functions import SendData
from Functions import GPS
from Functions import Tools
from Functions import Bluetooth
import machine,json,config
from machine import Pin

# Main function
if __name__ == "__main__":
    
    # Check if config button is pressed
    Button = Pin(3, Pin.OUT)
    Button.on()# PowerOn button
    ButtonLed = machine.Pin(5, machine.Pin.OUT)
    ConfigButton = Pin(4, Pin.IN, Pin.PULL_DOWN)
    if ConfigButton.value() == 1:
        if config.DEBUG: print("-> START CONFIG MODE")
        ButtonLed.on()
        Bluetooth.StartBLE()
    else:
        Button.off()
    
    if config.DEBUG: print("-> Start Data Sampling")
    ReadData.ReadData() # Read data from all the sensors
    
    if config.DEBUG: print("-> Connect to WIFI")
    connect = WifiTools.ConnectWifi() # Connect to WIFI
    
    if connect is True:
        if config.DEBUG: print("-> Successfully Connect to Wifi, now data will be send to the server")
        SendData.SendData() # Send data to the server
        if config.DEBUG: print("-> Disconnect from WIFI")
        WifiTools.DisconnectWifi() #Disconnect from WIFI
    
    # Check GPS
    with open('data/info.json') as f:
        info = json.load(f)
    f.close()
    if info["TodaySamplings"] == 24:
        if config.DEBUG: print("-> It's time to do some cleaning in the logs")
        Tools.LogCleaner() # Clear log files
        if config.DEBUG: print("-> Where are you? I will find you with GPS..")
        GPS.readGPSdata() # One time a day check the GPS
    
    if config.DEBUG: print("-> Going to sleep!Bye!")
    #DeepSleep
    machine.deepsleep(1800000)
    