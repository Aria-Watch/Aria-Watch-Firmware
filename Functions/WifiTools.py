'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import time,network,json,config,machine
from .Tools import *
from .SensorMng import *
 
def ConnectWifi():
    status = False
    wlan = network.WLAN(network.STA_IF)  # Create WLAN 
    wlan.active(True)  # Activate WLAN
    max_attempts = 3
    try:
        if not wlan.isconnected():  # Check if connected
            wlan.connect(config.WIFI,config.WIFI_PASS)# Connect
            time.sleep(2)
            attempt = 1
            while not wlan.isconnected():  # wait connection
                if attempt > max_attempts:
                    #print("Failed to connect after", max_attempts, "attempts")
                    LogMaster("Failed to connect to WIFI after 3 attemps","WIFI",0)
                    break
                time.sleep(5)  # sleep
                attempt += 1

        if wlan.isconnected():
            status = True
            LogMaster("WIFI connected! config:" + str(wlan.ifconfig()) ,"WIFI",0)
        else:
            return
    except OSError as e:
        LogMaster("Failed to connect to WIFI! Error: " + str(e),"WIFI",0)
    return(status)


def DisconnectWifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()

