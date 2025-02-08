'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''
import scd4x,machine,time,dht,config
from pms5003 import PMS5003
from bme import *
from .Tools import *
from .ErrorHandling import *

def ReadCO2(pres):
    if config.DEBUG: print("-> Read CO2")
    try:
        i2c = machine.I2C(1, sda=machine.Pin(8), scl=machine.Pin(9), freq=100000) 
        scd4x_sensor = scd4x.SCD4X(i2c) #Inizializzazione sensore
        scd4x_sensor.set_ambient_pressure(pres)
        scd4x_sensor.start_periodic_measurement() #Modalità lettura
        time.sleep(5)
        for i in range(3) :
            time.sleep(3)
            CO2 = scd4x_sensor.co2
            temp = round(scd4x_sensor.temperature, 2)
            hum = round(scd4x_sensor.relative_humidity, 2)
        scd4x_sensor.stop_periodic_measurement()
    except Exception as e:
        LogMaster("Error in CO2 Sensor! Error: " + str(e),"Error",1)
    if config.DEBUG: print("-> CO2:" + str(CO2) + " temp:" + str(temp) + " hum:"+ str(hum))
    return(CO2,temp,hum)
    
    
def ReadPmData():
    if config.DEBUG: print("-> Read PM")
    try:
        pms5003 = PMS5003(
            uart=machine.UART(1, tx=14, rx=13, baudrate=9600),
            pin_enable=machine.Pin(15),
            pin_reset=machine.Pin(12),
            mode="active"
        )
        for i in range(3) :
            pm1 = pms5003.read().pm_ug_per_m3(1.0, True)
            pm2 = pms5003.read().pm_ug_per_m3(2.5, True)
            pm10 = pms5003.read().pm_ug_per_m3(True)
            time.sleep(3)
    except Exception as e:
        LogMaster("Error in PM Sensor! Error: " + str(e),"Error",1)
    if config.DEBUG: print("-> pm1:" + str(pm1) + " pm2:" + str(pm2) + " pm10:"+ str(pm10))
    return(pm1,pm2,pm10)


def ReadDHT22():
    if config.DEBUG: print("-> Read Temp and Hum")
    try:
        sensor = dht.DHT22(machine.Pin(0))
        for i in range(3) :
            time.sleep(1)
            sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
    except Exception as e:
        LogMaster("Error in TEMP-HUM Sensor! Error: " + str(e),"Error",1)
    if config.DEBUG: print("-> temp:" + str(temp) + " hum:" + str(hum))
    return(temp,hum)


def ReadVOC():
    if config.DEBUG: print("-> Read VOC")
    try:
        i2c0 = machine.I2C(1, scl = machine.Pin(9), sda = machine.Pin(8), freq = 400000)
        bme = BME680_I2C(i2c=i2c0)
        bme.sea_level_pressure = 1002 # Mettere questo campo in base alla posizione del GPS 
        for i in range(3) :
            time.sleep(1)
            temp = str(round(bme.temperature, 2))
            hum = str(round(bme.humidity, 2))
            pres = str(round(bme.pressure, 2))
            #gas = str(round(bme.gas/1000, 2))
            gas = str(round(bme.gas/100, 2))
            alt = str(round(bme.altitude, 2))
    except Exception as e:
        LogMaster("Error in VOC Sensor! Error: " + str(e),"Error",1)
    if config.DEBUG: print("-> temp:" + str(temp) + " hum:" + str(hum)+ " pres:" + str(pres)+ " gas:" + str(gas)+ " alt:" + str(alt))       
    return(temp,hum,pres,gas,alt)




def ReadCO():
    uart = machine.UART(1, baudrate=9600, tx=41, rx=40,bits=8, parity=None, stop=1)
    while True:
        if uart.any():
            # Read the data from UART
            sensor_data = uart.read(9)  # Reading 9 bytes as per the given protocol
            if sensor_data[0] == 0xFF:
                concentration_high = sensor_data[4]
                concentration_low = sensor_data[5]
                concentration = (concentration_high * 256) + concentration_low
                return concentration
            else:
                ErrorHandling.LogMaster("Error in CO Sensor! Error: Invalid start byte received from sensor.","Error",1)
                return


def ReadMQ4():
    # --- TO check and improve ALL
    sensor_pin = machine.ADC(machine.Pin(3))
    calibration_factor = 6.0
    sensor_value = sensor_pin.read()
    voltage = sensor_value * 5 / 1024.0
    ppm = voltage / calibration_factor
    return(ppm)
