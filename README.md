# AriaWatch Device Firmware

## Overview

This repository contains the MicroPython firmware for AriaWatch air quality monitoring devices. AriaWatch is a global initiative to combat climate change misinformation by providing accurate, real-time air quality data through a network of solar-powered monitoring devices.

The firmware supports reading data from multiple environmental sensors and transmitting it securely to the AriaWatch cloud platform.

## Supported Device Models

Currently supports two device models:
- **Bora**: Full-featured model with complete sensor suite
- **Borino**: Compact model with essential sensors

## Features

- Solar power management
- Multiple sensor integration (PM, CO, CH4, temperature, humidity)
- Secure WiFi connectivity
- Cloud data transmission
- OTA (Over-The-Air) updates
- Weather-resistant operation
- Sensor calibration

## Initial Configuration

After flashing the firmware, create a `first_boot.json` file with the following configuration:

```json
{
    "Device_Model": "Borino",     // "Borino" or "Bora"
    "User_Email": "user@gmail.com", // Account email for device association
    "WIFI_SSID": "xx",              // WiFi network name
    "WIFI_PASS": "yy",              // WiFi password
    "PM": false,                  // Enable if PM sensor present
    "CO": false,                  // Enable if CO sensor present
    "CH4": false,                 // Enable if CH4 sensor present
    "DHT22": false                // Enable if DHT22 sensor present
}
```

## Supported Sensors

The firmware can interface with the following sensors:
- Particulate Matter (PM1, PM2.5, PM10)
- Carbon Monoxide (CO)
- Methane (CH4)
- Temperature and Humidity (DHT22)
- Volatile Organic Compounds (VOC)
- Atmospheric Pressure

## Development Roadmap

Current development priorities:
- [ ] Enhanced logging system
- [ ] Improved OTA update mechanism
- [ ] Sensor calibration functions
- [ ] Optimized sensor reading system
- [ ] Extended error handling
- [ ] Battery management improvements

## Technical Details

The device firmware handles:
- Sensor initialization and regular reading
- Data validation and preprocessing
- Power management for solar operation
- Network connectivity
- Secure data transmission
- Device health monitoring
- Automatic updates

## Contributing

We welcome contributions to improve the firmware. Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with your changes

## License

[License information to be added]

## About AriaWatch

AriaWatch is a project dedicated to providing accurate air quality data worldwide. The devices form a global network of environmental monitoring stations, contributing to climate change research and environmental policy evaluation. For more information, visit [www.aria.watch](https://www.aria.watch).