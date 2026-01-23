# Yahboom RGB Cooling HAT Controller for Home Assistant

This Home Assistant add-on controls the **Yahboom RGB Cooling HAT** for Raspberry Pi. It manages active cooling (fan speed) based on CPU temperature, provides RGB LED status control, and displays system information on the integrated OLED display.

## Technical Specifications (I2C)

The add-on communicates with the HAT via the I2C bus. The following I2C addresses are used:

 | Component | I2C Address | Function | 
 | :--- | :--- | :--- | 
 | **MCU (Fan/RGB)** | `0x0d` | Controls fan speed and RGB LED modes/colors. | 
 | **OLED Display** | `0x3c` | 128x32 SSD1306 display for system info. | 


### Fan Speed Thresholds
* **Temp < 40°C**: Fan Off (Speed 0)
* **Temp ≥ 40°C**: Speed 2
* **Temp ≥ 45°C**: Speed 5
* **Temp ≥ 50°C**: Max Speed 9


## Installation

1. **I2C Activation**: Enable I2C on your Raspberry Pi.
2. **Add-on Configuration**: Your `config.json` must include:
   ```json
   "devices": ["/dev/i2c-1:/dev/i2c-1:rwm"]
   ```

### Troubleshooting

*** IP Address not displaying:** The add-on uses a socket-based method to ensure compatibility with BusyBox (Alpine Linux).