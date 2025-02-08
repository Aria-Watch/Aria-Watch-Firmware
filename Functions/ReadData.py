import json, config, time
from Functions.Sensors import ReadCO, ReadDHT22, ReadPmData, ReadVOC, ReadCO2, ReadMQ4
from Functions.Tools import SaveSensorData, UpdateSampling, PowerMng,batteryInfo
from Functions.LedMng import set_led

class SensorManager:
    def __init__(self):
        self.data = {"Device": config.DEVICE_ID, "SV": config.FIRMWARE,"Email": config.EMAIL,"Key": config.KEY}
        self.debug = config.DEBUG
        
    def _debug_print(self, message):
        if self.debug:
            print(f"-> {message}")

    def _operate_fan(self):
        self._debug_print("Start FAN to change the air inside the device")
        PowerMng("on", "FAN")
        time.sleep(4)
        PowerMng("off", "FAN")
        self._debug_print("FAN stop")

    def read_battery(self):
        self._debug_print("Start reading battery data")
        self.data["BT"] = batteryInfo()
        self._debug_print(f"vbatt: {self.data['BT']}")

    def read_3v_sensors(self):
        self._debug_print("Start read 3V sensor data")
        if config.DEVICE_MODEL == "Bora" : PowerMng("on", "Sensors3V")
        try:
            # DHT22 sensor (optional)
            if config.DHT22:
                temp, hum = ReadDHT22()
                self.data.update({"Temp": temp, "Hum": hum})
            
            # VOC sensor
            tempVOC, humVOC, pres, gas, alt = ReadVOC()
            self.data.update({
                "TempVOC": float(tempVOC),
                "HumVOC": float(humVOC),
                "PressureVOC": float(pres),
                "VOC": float(gas)
            })
            
            # CO2 sensor
            co2, temp_1, hum_1 = ReadCO2(int(float(pres)))
            self.data.update({
                "CO2": co2,
                "TempCO2": temp_1,
                "HumCO2": hum_1
            })
            if co2 >= 1500:
                set_led((30, 0, 0))
            elif co2 >= 1000:
                set_led((30, 10, 0))
            else:
                set_led((0, 30, 0))
        finally:
            PowerMng("off", "Sensors3V")

    def read_5v_sensors(self):
        self._debug_print("Start read 5V sensor data")
        if config.DEVICE_MODEL == "Bora":
            PowerMng("on", "5V")
            PowerMng("on", "Sensors5V")
        try:
            # PM sensor (optional)
            if config.PM:
                pm1, pm2, pm10 = ReadPmData()
                self.data.update({
                    "PM1": pm1,
                    "PM2": pm2,
                    "PM10": pm10
                })
            
            # CO sensor (optional)
            if config.CO:
                self.data["CO"] = ReadCO()
            
            # CH4 sensor (optional)
            if config.CH4:
                self.data["CH4"] = round(ReadMQ4(), 2)
        finally:
            if config.DEVICE_MODEL == "Bora": 
                PowerMng("off", "Sensors5V")
                PowerMng("off", "5V")

    def read_gps_data(self):
        with open('data/gps.json') as f:
            gpsdata = json.load(f)["GPS"][-1]
            self.data.update({
                "Lat": gpsdata["latitude"],
                "Long": gpsdata["longitude"]
            })

    # Collect data from sensors
    def collect_data(self):
        if config.DEVICE_MODEL == "Bora" : 
            self.read_battery()
            self._operate_fan()
            self.read_gps_data()

        self.read_3v_sensors()
        self.read_5v_sensors()
        self._debug_print("Save data and update info")
        SaveSensorData(self.data)
        UpdateSampling()

def ReadData():
    sensor_manager = SensorManager()
    sensor_manager.collect_data()