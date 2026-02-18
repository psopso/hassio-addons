# Suptronics X728 GPIO Button Manager

This Home Assistant add-on provides safe shutdown and reboot handling for the **Suptronics / Geekworm X728 UPS board** on Raspberry Pi.

It solves two main problems:

* Properly reacts to the **hardware power button** on the X728 board
* Automatically shuts down the system when the **battery voltage drops too low**

The add-on runs independently of Home Assistant core logic and communicates directly with:
* GPIO pins (button and power control)
* I²C battery monitor (MAX17040)

---

## What this add-on does

The add-on monitors:

* **GPIO5** – X728 button signal  
* **GPIO12** – X728 power management enable pin  
* **I²C MAX17040** – battery voltage sensor  

Based on these signals, it decides whether to:

* Reboot the system
* Shut down the system safely
* Power off the X728 board after shutdown (optional)

---

## Button behavior (GPIO5)

The X728 board generates a signal on GPIO5 when the physical button is pressed.

This add-on measures how long the signal stays HIGH and reacts as follows:

| Button press duration | Action |
|-----------------------|--------|
| 0.2 – 0.6 seconds     | Reboot host |
| longer than 0.6 sec   | Shutdown host |

### Explanation

* Short press → system reboot  
* Long press → system shutdown  
* The shutdown is executed using the Supervisor API (`/host/shutdown`)  
* No direct GPIO power cut is done by default (to avoid data corruption)

---

## Low battery behavior (I²C)

The add-on periodically reads battery voltage from the MAX17040 chip via I²C.

Default behavior:

* Voltage is checked every **10 seconds**
* If voltage drops below **3.4 V**, shutdown is triggered

| Condition | Action |
|-----------|--------|
| Voltage > 3.4 V | Normal operation |
| Voltage ≤ 3.4 V | Shutdown host |

This prevents filesystem corruption and protects the battery from deep discharge.

### Voltage filtering

Transient read errors (for example 0.0 V readings) are ignored and do not immediately trigger shutdown.

---

## GPIO control (PIN_ENABLE)

GPIO12 is set to HIGH at startup to enable proper power management on the X728 board.

Optional power cut after shutdown can be enabled using:

```
dtoverlay=gpio-poweroff,gpiopin=13,active_delay_ms=6500,inactive_delay_ms=4000,timeout_ms=20000
```

(Disabled by default)

---

## Requirements

* Raspberry Pi with Suptronics / Geekworm X728 UPS
* Home Assistant OS
* I²C enabled
* MAX17040 present on I²C bus 1 at address `0x36`

---

## Installation

1. Copy the add-on directory into:

```
/addons/x728_gpio_button_manager
```

2. Add it as a local repository in Home Assistant:
   * Settings → Add-ons → Add-on Store → Repositories

3. Install and start the add-on

4. Enable I²C in your system

---

## Safety notes

* This add-on controls host power state
* Wrong GPIO configuration may cause power loss
* Test on a non-critical system first

---

## Summary

This add-on provides:

✔ Safe shutdown using the X728 hardware button  
✔ Automatic shutdown on low battery  
✔ Independent operation from Home Assistant core  
✔ No reliance on Home Assistant automations  

It turns the X728 board into a reliable UPS controller for Home Assistant OS.

