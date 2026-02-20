import gpiod
from gpiod.line import Direction, Edge, Value
import time
import sys
import requests
from smbus2 import SMBus
import paho.mqtt.client as mqtt

# ---------------- CONFIG ----------------

CHIP_ID = 0
PIN_BUTTON = 5
PIN_ENABLE = 12

REBOOT_MIN = 0.2
REBOOT_MAX = 0.6
SHUTDOWN_MIN = 0.6

I2C_BUS = 1
MAX17040_ADDR = 0x36
VOLTAGE_REG = 0x02

LOW_VOLTAGE = 3.4
CHECK_INTERVAL = 10
PRINT_CHECK_INTERVAL = 120

# MQTT
MQTT_HOST = "core-mosquitto"
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASS = None
MQTT_PREFIX = "x728"

token = sys.argv[1]

# ---------------------------------------

def run_command(action):
    url = f"http://supervisor/host/{action}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    print(f"[X728] Request: {action}", flush=True)
    try:
        r = requests.post(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[X728] API error: {r.status_code} {r.text}", flush=True)
    except Exception as e:
        print(f"[X728] API exception: {e}", flush=True)

def read_voltage(bus):
    data = bus.read_i2c_block_data(MAX17040_ADDR, VOLTAGE_REG, 2)
    raw = (data[0] << 8) | data[1]
    voltage = raw * 1.25 / 1000 / 16
    return round(voltage, 2)

def mqtt_connect():
    client = mqtt.Client(
        client_id="x728-addon",
        protocol=mqtt.MQTTv311,
        callback_api_version=4
    )

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    return client

def mqtt_publish(client, topic, value):
    full_topic = f"{MQTT_PREFIX}/{topic}"
    client.publish(full_topic, value, retain=True)

def main():
    print("[X728] Startuji manager (MQTT verze)...", flush=True)

    bus = SMBus(I2C_BUS)
    mqtt_client = mqtt_connect()

    configs = {
        PIN_BUTTON: gpiod.LineSettings(
            direction=Direction.INPUT,
            edge_detection=Edge.BOTH
        ),
        PIN_ENABLE: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.ACTIVE
        )
    }

    last_check = 0
    last_print_check = 0
    shutdown_sent = False

    with gpiod.request_lines(
        f"/dev/gpiochip{CHIP_ID}",
        consumer="x728-manager",
        config=configs
    ) as lines:

        print(f"[X728] GPIO{PIN_ENABLE} = ACTIVE", flush=True)
        mqtt_publish(mqtt_client, "status", "online")

        while True:
            now = time.time()

            # ---------- I2C BATTERY ----------
            if now - last_check > CHECK_INTERVAL:
                last_check = now
                try:
                    voltage = read_voltage(bus)
                    mqtt_publish(mqtt_client, "battery/voltage", voltage)

                    if now - last_print_check > PRINT_CHECK_INTERVAL:
                        print(f"[X728] Battery voltage: {voltage} V", flush=True)
                        last_print_check = now

                    if voltage <= LOW_VOLTAGE and not shutdown_sent:
                        print("[X728] Low voltage -> SHUTDOWN", flush=True)
                        mqtt_publish(mqtt_client, "event", "low_battery_shutdown")
                        run_command("shutdown")
                        shutdown_sent = True

                except Exception as e:
                    print(f"[X728] I2C error: {e}", flush=True)

            # ---------- GPIO BUTTON ----------
            if lines.wait_edge_events(timeout=0.5):
                for event in lines.read_edge_events():

                    if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                        start_time = time.time()
                        mqtt_publish(mqtt_client, "button", "pressed")
                        print("[X728] Button HIGH", flush=True)

                        while True:
                            val = lines.get_value(PIN_BUTTON)
                            elapsed = time.time() - start_time

                            if elapsed > SHUTDOWN_MIN and not shutdown_sent:
                                print("[X728] Long press -> SHUTDOWN", flush=True)
                                mqtt_publish(mqtt_client, "event", "button_shutdown")
                                run_command("shutdown")
                                shutdown_sent = True

                            if val == Value.INACTIVE:
                                mqtt_publish(mqtt_client, "button", "released")
                                print(f"[X728] Button LOW ({elapsed:.2f}s)", flush=True)

                                if REBOOT_MIN <= elapsed <= REBOOT_MAX:
                                    mqtt_publish(mqtt_client, "event", "button_reboot")
                                    run_command("reboot")
                                break

                            time.sleep(0.05)

            time.sleep(0.1)

if __name__ == "__main__":
    main()

# dtoverlay=gpio-poweroff,gpiopin=13,active_delay_ms=6500,inactive_delay_ms=4000,timeout_ms=20000