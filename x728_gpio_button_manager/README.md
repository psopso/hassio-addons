# Suptronics X728 GPIO Button Manager (Home Assistant Add-on)

This add-on provides safe OS-level power management for the Suptronics / Geekworm X728 UPS board
when used with Home Assistant OS on Raspberry Pi.

Features:
- Detects short press ‚Üí reboot
- Detects long press ‚Üí shutdown
- Monitors battery voltage via I2C (MAX17040)
- Automatic shutdown on low voltage
- Works independently of Home Assistant

GPIO:
Button: GPIO5
Enable: GPIO12

Button logic:
Short press (0.2‚Äď0.6s) ‚Üí reboot
Long press (>0.6s) ‚Üí shutdown

Battery threshold:
LOW_VOLTAGE = 3.4V

Optional poweroff overlay:
dtoverlay=gpio-poweroff,gpiopin=13,active_delay_ms=6500,inactive_delay_ms=4000,timeout_ms=20000
