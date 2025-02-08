# This file is executed on every boot (including wake-boot from deepsleep)

import esp,gc,machine,time,os
import config
from Functions.Tools import first_boot

if "first_boot.json" in os.listdir():
    first_boot()

gc.collect() # Garbage collector
esp.osdebug(None) # Disable Debug

# PIN Creation and attribution

if config.DEVICE_MODEL == "Bora":
    Power_Button = machine.Pin(2, machine.Pin.OUT)
    Power_Button.on()

    Mosfet_3V_Sensors = machine.Pin(39, machine.Pin.OUT)
    Mosfet_3V_Sensors.off()

    Mosfet_GPS = machine.Pin(35, machine.Pin.OUT)
    Mosfet_GPS.off()

    LDO_5V = machine.Pin(17, machine.Pin.OUT)
    LDO_5V.off()

    Mosfet_5V_Sensors = machine.Pin(21, machine.Pin.OUT)
    Mosfet_5V_Sensors.off()

    Mosfet_12V = machine.Pin(16, machine.Pin.OUT)
    Mosfet_12V.off()

    SettingButtonLed = machine.Pin(5, machine.Pin.OUT)
    SettingButtonLed.off()

    SettingButton1= machine.Pin(3, machine.Pin.OUT)
    SettingButton2= machine.Pin(4, machine.Pin.OUT)
    SettingButton1.off()
    SettingButton2.off()
    time.sleep(3)
    Power_Button.off()