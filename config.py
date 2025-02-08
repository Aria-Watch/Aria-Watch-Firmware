import json

with open('data/wifi.json') as f:
    config = json.load(f)
    
with open('data/version.json') as f:
    version = json.load(f)

WIFI = config['WIFI']
WIFI_PASS = config['WIFI_PASS']
FIRMWARE = version['FVersion']
DEVICE_ID = "XXXX"
API_URL = "https://data.aria.watch/receive"
DEBUG = False
OTA_UPDATE = True