'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import urequests, json, ubinascii,config
from .Tools import *
from .Update import *
from .SensorMng import *

def SendData():
    
    # Read last data
    with open('data/sensor.json', 'r') as f:
        file_data2 = json.load(f)
        data = json.dumps(file_data2["DATA"][-1])
    f.close()
  
    data64 = ubinascii.b2a_base64(bytes(str(data),'UTF-8')) # base64 encode
    Result = ''
    
    try:
        r = urequests.post(config.API_URL, data = data64) #Send Data
        Result = r.json()
        r.close()
        if str(Result['result']) == "ok":
            set_rtc_from_json(Result)
            LogMaster("Data sent to the server with success!","Sent",0)
            
            #Check if is available a new update
            if config.OTA_UPDATE and str(Result['DeviceVersion']) != config.FIRMWARE:
                Update(str(Result['DeviceVersion']))
        else:
            LogMaster("Error from the data server!" + str(e),"Error",1)
    except Exception as e:
        LogMaster("Error when sending data to the server! Error:" + str(e),"Error",1)

        
    # Check server response, log if error or correct
    
            