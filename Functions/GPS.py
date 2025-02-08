'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import time, json ,machine,config
from .Tools import *
from .ErrorHandling import *

def readGPSdata():
    if config.DEBUG: print("-> Start to read GPS")
    GPSData = False
    PowerMng("on","5V")
    PowerMng("on","GPS")# Power on GPS
    timeout = time.time() + 900 # Timeout 15 minutes

    gps_input= machine.UART(1,baudrate=9600, rx=44,tx=43,timeout=1000,timeout_char=50) # GPS serial
    while time.time() < timeout:
        buff = str(gps_input.readline()) # dato del GPS
        parts = buff.split(',')
        if (parts[0] == "b'$GPGGA" and len(parts) == 15 and parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):     
            latitude = convertToDigree(parts[2])
            if (parts[3] == 'S'):
                latitude = -latitude
            longitude = convertToDigree(parts[4])
            if (parts[5] == 'W'):
                longitude = -longitude
            satellites = parts[7]
            altitude = parts[9]
            WGS84  = parts[11]
            gpsTime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
            datajson = {"latitude":latitude,"longitude":longitude,"altitude":altitude,"WGS84":WGS84,"nsat":satellites,"gpsTime":gpsTime,"timestamp":time.time()}
            GPSData = True
            saveGPSdata(datajson)
            time.sleep(2)
            
    PowerMng("off","GPS")
    PowerMng("off","5V")# Turnoff the GPS
    
    if GPSData is True:
        LogMaster("Successfully retrive GPS data!","GPS",0)
        if config.DEBUG: print("-> Successfully retrive GPS data! " + str(datajson))
    else:
        LogMaster("No GPS data!","GPS",0)
        if config.DEBUG: print("-> No GPS data!")
  
  
def saveGPSdata(data):
    with open('data/gps.json', 'r+') as f:
        file_data = json.load(f)
        file_data["GPS"].append(data)
        f.seek(0)
        if len(file_data["GPS"]) > 10:
            file_data["GPS"] = file_data["DATA"][-10:]
            
        file_data["GPS"].append(data)
        with open('data/gps.json', 'w') as f:
            json.dump(file_data, f)
            
    
def convertToDigree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) #degrees
    nexttwodigits = RawAsFloat - float(firstdigits*100) #minutes
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) # to 6 decimal places
    return str(Converted)


