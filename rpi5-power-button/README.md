# RPi 5 Power Button


The Addon listens to the Power Button Device of the Raspberry Pi 5. A short press <= 2s always emits an event like:

```yml
event_type: power_button
data:
  state: short_press
````

The long press duration can be configured between 3 and 10 seconds and its behaviour can be set to "shutdown", "reboot", "reload" and "none".
Selecting "none" results in sending an event like this:

```yml
event_type: power_button
data:
  state: long_press
  duration: "3.18"
  threshold: 3
  button_type: long_press
```



