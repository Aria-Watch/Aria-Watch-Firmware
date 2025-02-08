'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import machine,json,time,struct,random,bluetooth
from ble_advertising import advertising_payload
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheral:
    def __init__(self, ble, name="Bora_123"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            #print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            #print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        #print("Starting advertising") 
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback


def StartBLE():
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)
    
    def on_rx(v):
        tmp_wifi = ''
        tmp_pass = ''
        string = v.decode("utf-8")
        CommandReceived = str(string.strip())
        #print(CommandReceived)
        #print("RX:", string)
        
        if CommandReceived[:7] == "SetWifi":
            #Read WIFI ssid
            with open('data/wifi.json') as f:
                config = json.load(f)
            config['WIFI'] = CommandReceived[8:]
            with open('data/wifi.json', 'w') as f:
                json.dump(config, f)
                f.close()
        elif CommandReceived[:8] == "SetWPass":
            #read WIFI password and update config
            tmp_pass = CommandReceived[9:]
            with open('data/wifi.json') as f:
                config = json.load(f)
            config['WIFI_PASS'] = CommandReceived[9:]
            with open('data/wifi.json', 'w') as f:
                json.dump(config, f)
                f.close()
            machine.reset()
        else:
            DataMng(CommandReceived,p)
        
    p.on_write(on_rx)

# keep BLE active ## To improve
    while True:
        if p.is_connected():
            x=0
        time.sleep_ms(100)


def DataMng(received,p):
    last_lines = []
    TheFile = ""
    if received == "ReadError":
        TheFile = "data/log/error.log"
    elif received == "ReadWifi":
        TheFile = "data/log/wifi.log"
    elif received == "ReadGPS":
        TheFile = "data/log/gps.log"
    elif received == "ReadLogs":
        TheFile = "data/log/sent.log"
    else:
        p.send("Command Not Found!")
        return
    
    # read file last 5 line
    with open(TheFile, 'r') as file:        
        for line in file:
            last_lines.append(line.strip()) 
            if len(last_lines) > 5:
                last_lines.pop(0)
    
    #send back the last 5 line of the file
    length = len(last_lines)
    for x in range(length):
        p.send(last_lines[x])
        p.send("\n")
        if x == (length - 1):
            p.send("END")

