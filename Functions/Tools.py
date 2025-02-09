import machine,json,os,random,hashlib
from machine import RTC, ADC, reset

def UpdateSampling():
    with open('data/info.json') as f:
        config = json.load(f)
    config["TodaySamplings"] += 1
    config["TotalSamplings"] += 1
    if config["TodaySamplings"] == 48 :
        config["TodaySamplings"] = 0
    with open('data/info.json', 'w') as f:
        json.dump(config, f)
        f.close()
    f.close()

    
def SaveSensorData(data):
    with open('data/sensor.json', 'r+') as f:
        file_data = json.load(f)
        # Mantieni solo gli ultimi elementi
        if len(file_data["DATA"]) > 20:
            file_data["DATA"] = file_data["DATA"][-20:]
        file_data["DATA"].append(data)
        f.seek(0)
        f.close()
        with open('data/sensor.json', 'w') as f:
            json.dump(file_data, f)
        f.close()
        
def batteryInfo():
    adc = machine.ADC(machine.Pin(1, mode=machine.Pin.IN))  # Assign the ADC pin to read, set it to input mode
    adc.atten(ADC.ATTN_11DB)    
    measuredvbat = ((adc.read() / 4095) * 3.3 * 2 * 1.03) # Find the voltage, 1.03 is a fudge factor, calibrated with multimeter
    return(measuredvbat)


#Function to manage the power of Mosfet and LDO 
def PowerMng(Action,Element):
    
    Mosfet_3V_Sensors = machine.Pin(39, machine.Pin.OUT)
    Mosfet_GPS = machine.Pin(35, machine.Pin.OUT)
    LDO_5V = machine.Pin(17, machine.Pin.OUT)
    Mosfet_5V_Sensors = machine.Pin(21, machine.Pin.OUT)
    Mosfet_12V = machine.Pin(16, machine.Pin.OUT)

    if Action == "on":
        if Element == "Sensors3V":
            Mosfet_3V_Sensors.on()
        elif Element == "GPS":
            Mosfet_GPS.on()
        elif Element == "Sensors5V":
            Mosfet_5V_Sensors.on()
        elif Element == "5V":
            LDO_5V.on()
        elif Element == "FAN":
            Mosfet_12V.on()
        else:
            return
    elif Action == "off":
        if Element == "Sensors3V":
            Mosfet_3V_Sensors.off()
        elif Element == "GPS":
            Mosfet_GPS.off()
        elif Element == "Sensors5V":
            Mosfet_5V_Sensors.off()
        elif Element == "5V":
            LDO_5V.off()
        elif Element == "FAN":
            Mosfet_12V.off()
        else:
            return
    else:
        return
    
    
def GetTime():
    rtc = machine.RTC()
    timestamp=rtc.datetime() # Read current time
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
    return(timestring)
        
        
        
def LogCleaner():
    logfiles = [
        'data/log/error.log',
        'data/log/sent.log',
        'data/log/gps.log',
        'data/log/wifi.log'
    ]
    
    for logfile in logfiles:
        with open(logfile, 'r') as file:
            lines = file.readlines()
        if len(lines) > 1000:
            with open(logfile, 'w') as file:
                file.writelines(lines[100:])  


def set_rtc_from_json(json_data):
    # Assumi che json_data sia un dizionario decodificato contenente il risultato del POST
    try:
        # Estrai il campo 'date' dal JSON
        date_str = json_data.get("date", "")  # Ottieni la data come stringa

        # Converti la stringa della data in una tupla (anno, mese, giorno, ora, minuto, secondo, microsecondo, tzinfo)
        # Assumi che la data sia nel formato "YYYY:MM:DD HH:MM:SS"
        parts = date_str.replace(':', '-').replace(' ', '-').split('-')
        if len(parts) == 6:  # Assicurati che ci siano abbastanza parti per anno, mese, giorno, ecc.
            year, month, day, hour, minute, second = [int(part) for part in parts]

            # Imposta l'RTC con la data e l'ora
            rtc = RTC()
            rtc.datetime((year, month, day, 0, hour, minute, second, 0))
            #print("RTC updated to:", rtc.datetime())
        else:
            with open('data/log/error.log', 'a+b') as f:
                f.write("\n" + "["+ str(GetTime()) +"] -> Failed to set RTC: " + str(e))
            f.close()
            
    except Exception as e:
        with open('data/log/error.log', 'a+b') as f:
            f.write("\n" + "["+ str(GetTime()) +"] -> Failed to set RTC: " + str(e))
        f.close()
        
# Function to set the first boot configuration       
def first_boot():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    with open("first_boot.json", 'r') as f:
        config = json.load(f)
    with open("data/info.json", 'r') as f:
        info = json.load(f)
    with open("data/wifi.json", 'r') as f:
        wifi = json.load(f)

    for key in config:
        if key in info:
            info[key] = config[key]
        if key in wifi:
            wifi[key] = config[key]

    random_string = ''.join(random.choice(chars) for _ in range(12))
    hash_object = hashlib.sha256()
    hash_object.update(random_string.encode())
    hash_object = hashlib.sha256(random_string.encode())
    hash_bytes = hash_object.digest()
    hash_hex = ''.join(['{:02x}'.format(b) for b in hash_bytes])
    info["ID"] = str(config["Device_Model"]) + "_" + str(random_string)
    info["Device_Key"] = str(hash_hex[:12])

    #Save the new configuration        
    with open("data/info.json", 'w') as f:
        json.dump(info, f)
    with open("data/wifi.json", 'w') as f:
        json.dump(wifi, f)
    #Remove the first_boot.json file
    os.remove("first_boot.json")
    reset()