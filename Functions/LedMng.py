from machine import Pin
from neopixel import NeoPixel
import config

def set_led(color):
    np = NeoPixel(Pin(config.LED_PIN, Pin.OUT), 1)
    np[0] = color
    np.write()