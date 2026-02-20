# Suptronics X728 GPIO Button Manager

This Home Assistant add-on provides safe system shutdown and reboot handling for the **Suptronics / Geekworm X728 UPS HAT** on Raspberry Pi.

It monitors:
- the physical power button (GPIO5)
- power loss (GPIO6)
- the battery voltage via I²C (MAX17040 fuel gauge)

and performs controlled shutdown or reboot using the Home Assistant Supervisor API.

---

## Features

- Short button press → system reboot
- Long button press → system shutdown
- Automatic shutdown on low battery voltage
- Safe OS shutdown (no hard power cut)
- Keeps UPS enabled using GPIO12

---

## Button Behavior

| Action | Button | GPIO5 Signal | Result |
|--------|------|-------|--------|
| Short press | 1 – 2 s | 0.2 – 0.6 s pulse | Reboot |
| Longer press | 3 – 7 s | > 0.6 s pulse | Shutdown |
| Long press | >8 s | ------------------ | Force Shutdown immediately |

GPIO12 is forced HIGH to allow the X728 to report button presses correctly.

---

## Low Battery Protection

The add-on reads battery voltage from the MAX17040 chip via I²C.

If voltage falls below configured threshold:
```
LOW_VOLTAGE = 3.4 V
```
The system will:
1. Trigger Home Assistant shutdown
2. Allow OS to power down safely

## MQTT Sensors

This addon publishes several MQTT topics that can be used as Home Assistant sensors:

- `x728/battery_voltage` – current battery voltage (V)
- `x728/button` – button state (`pressed` / `released`)
- `x728/event` – events:
  - `short_press_reboot`
  - `long_press_shutdown`
  - `low_battery_shutdown`
  - `power_loss`
- `x728/status` – addon status (`online`)

These topics can be mapped to Home Assistant MQTT sensors in `configuration.yaml`.

Example:

```yaml
mqtt:
  sensor:
    - name: "X728 Battery Voltage"
      state_topic: "x728/battery_voltage"
      unit_of_measurement: "V"
      unique_id: "x728_battery_voltage"
      device:
        identifiers: ["x728_ups"]
        name: "X728 UPS"
        model: "X728"
        manufacturer: "Geekworm"

    - name: "X728 Battery Capacity"
      state_topic: "x728/battery_capacity"
      unit_of_measurement: "%"
      unique_id: "x728_battery_capacity"
      device:
        identifiers: ["x728_ups"]
        name: "X728 UPS"
        model: "X728"
        manufacturer: "Geekworm"
        
  binary_sensor:
    - name: "X728 Power Loss"
      state_topic: "x728/power_loss"
      payload_on: "1"
      payload_off: "0"
      unique_id: "x728_power_loss"
      device:
        identifiers: ["x728_ups"]
        name: "X728 UPS"
        model: "X728"
        manufacturer: "Geekworm"
---

## Installation

1. Copy this add-on into:
```
/addons/local/x728_gpio_button_manager
```

2. Restart Supervisor

3. Install the add-on from Local Add-ons

4. Start add-on

---

## Requirements

- Raspberry Pi with X728 UPS
- Home Assistant OS or Supervised
- GPIO and I²C enabled
- MAX17040 fuel gauge available on I²C bus

---

## Safety Notes

- This add-on does NOT cut power directly.
- It relies on proper shutdown using Supervisor API.
- Optional GPIO power-off overlay can be enabled if desired.

---

## Optional Power Cut Overlay

Example config.txt:
```
dtoverlay=gpio-poweroff,gpiopin=13,active_delay_ms=6500,inactive_delay_ms=4000,timeout_ms=20000
```

---

## Disclaimer

Use at your own risk. Improper power handling can damage storage or data.

---

## License

MIT


