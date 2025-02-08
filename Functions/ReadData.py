'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import json,config,time
from .SensorMng import *
from .Tools import *

def ReadData():
    
    if config.DEBUG: print("-> Start reading battery data")
    battery = batteryInfo() #Read Battery data
    if config.DEBUG: print("-> vbatt:" + str(battery))
    
    if config.DEBUG: print("-> Start FAN to change the air inside the device")
    PowerMng("on","FAN")#Power on FAN
    time.sleep(4)
    PowerMng("off","FAN")#Power off FAN
    if config.DEBUG: print("-> FAN stop")
    
    if config.DEBUG: print("-> Start read 3V sensor data")
    PowerMng("on","Sensors3V")#Power on 3V Mosfet
    Temp,Hum = ReadDHT22() # Read DHT22 data
    tempVOC,humVOC,pres,gas,alt = ReadVOC() # Read VOC data
    co2,temp_1,hum_1 = ReadCO2(int(float(pres))) # Read CO2 data
    PowerMng("off","Sensors3V") #Power off 3V Mosfet
    
    if config.DEBUG: print("-> Start read 5V sensor data")
    PowerMng("on","5V")# Power on 5V LDO and Mosfet
    PowerMng("on","Sensors5V")
    pm1,pm2,pm10 = ReadPmData() # Read PM data
    CO = ReadCO() #Read CO data
    CH4 = ReadMQ4() #Read CH4 data
    PowerMng("off","Sensors5V")
    PowerMng("off","5V") # Power off 5V LDO and Mosfet
    
    
    #Read GPS info
    with open('data/gps.json') as f:
        GPSfile = json.load(f)
        gpsdata = GPSfile["GPS"][-1]
    
    if config.DEBUG: print("-> Collect all data in a JSON")
    #Format data as a json
    data = {"Device": config.DEVICE_ID,
            "CO2": co2,
            "Temp": Temp,
            "Hum":Hum,
            "TempCO2": temp_1,
            "HumCO2":hum_1,
            "PM1":pm1,
            "PM2":pm2,
            "PM10":pm10,
            "BT":battery,
            "SV":config.FIRMWARE,
            "Lat":gpsdata["latitude"],
            "Long":gpsdata["longitude"],
            "TempVOC" : float(tempVOC),
            "HumVOC" : float(humVOC),
            "PressureVOC":float(pres),
            "VOC":float(gas),
            "CO":CO,
            "CH4":round(CH4,2)}
    
    if config.DEBUG: print("-> Save data and update info")
    SaveSensorData(data) #Save data in a file
    UpdateSampling() #Update sampling info