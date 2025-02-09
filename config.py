# Configuration file for the Firmware
import json

def load_json(filename):
    with open(f'data/{filename}') as f:
        return json.load(f)

# Load configurations
config = load_json('wifi.json')
info = load_json('info.json')

# Device configuration
WIFI = config['WIFI_SSID']
WIFI_PASS = config['WIFI_PASS']
FIRMWARE = info['FW_VERSION']
DEVICE_MODEL = info['Device_Model']
DEVICE_ID = info['ID']
KEY = info['Device_Key']
EMAIL = info['User_Email']
API_URL = "https://data.aria.watch/"
DEBUG = False
OTA_UPDATE = False

# Device specific settings
DEVICE_SETTINGS = {
    "Bora": {
        "SLEEP_TIME": 1800000,
        "SDA_PIN": 8,
        "SCL_PIN": 9,
        "PM_CONFIG": {
            "TX": 14,
            "RX": 13,
            "EN": 15,
            "RST": 12
        }
    },
    "Borino": {
        "SLEEP_TIME": 600000,
        "SDA_PIN": 9,
        "SCL_PIN": 10,
        "PM_CONFIG": {
            "TX": 12,
            "RX": 13,
            "EN": 14,
            "RST": 11
        }
    }
}

# Set device specific configuration
device_config = DEVICE_SETTINGS.get(DEVICE_MODEL, DEVICE_SETTINGS["Borino"])
SLEEP_TIME = device_config["SLEEP_TIME"]
SDA_PIN = device_config["SDA_PIN"]
SCL_PIN = device_config["SCL_PIN"]
LED_PIN = 16

# PM Sensor configuration
PM = info['PM']
if PM:
    PM_TX = device_config["PM_CONFIG"]["TX"]
    PM_RX = device_config["PM_CONFIG"]["RX"]
    PM_EN = device_config["PM_CONFIG"]["EN"]
    PM_RST = device_config["PM_CONFIG"]["RST"]

# Optional sensors configuration
CO = info['CO']
CO_TX = 41
CO_RX = 40
DHT22 = info['DHT22']
DHT_PIN = 0
CH4 = info['CH4']
CH4_PIN = 3