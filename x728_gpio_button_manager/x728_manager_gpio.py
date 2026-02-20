import os
import gpiod
from gpiod.line import Direction, Edge, Value
import time
import sys
import requests
from smbus2 import SMBus
import paho.mqtt.client as mqtt

# --- KONFIGURACE GPIO ---
CHIP_ID = 0
PIN_BUTTON = 5
PIN_ENABLE = 12
PIN_POWERLOSS = 6   # GPIO6 = HIGH => power loss

REBOOT_MIN = 0.2
REBOOT_MAX = 0.6
SHUTDOWN_MIN = 0.6

# --- I2C ---
I2C_BUS = 1
MAX17040_ADDR = 0x36
VOLTAGE_REG = 0x02

LOW_VOLTAGE = 3.4
LOW_VOLTAGE_COUNT_LIMIT = 3   # kolik po sobe musi byt nizke
MIN_VALID_VOLTAGE = 1.0       # mene = chyba mereni

CHECK_INTERVAL = 10
PRINT_CHECK_INTERVAL = 120

# --- MQTT ---
MQTT_TOPIC_BASE = "x728"

token = sys.argv[1]

MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USERNAME")
MQTT_PASS = os.environ.get("MQTT_PASSWORD")

# ---------------- MQTT ----------------

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[X728] MQTT connected: {reason_code}", flush=True)
    client.publish(f"{MQTT_TOPIC_BASE}/status", "online", retain=True)

def mqtt_connect():
    print(f"[X728] MQTT broker: {MQTT_HOST}:{MQTT_PORT}", flush=True)

    client = mqtt.Client(
        client_id="x728-addon",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    if MQTT_USER and MQTT_PASS:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        print("[X728] MQTT auth enabled", flush=True)
    else:
        print("[X728] MQTT WITHOUT AUTH", flush=True)

    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    return client

# ---------------- HOST CONTROL ----------------

def run_command(action):
    url = f"http://supervisor/host/{action}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    print(f"[X728] Pozadavek na {action} hostitele...", flush=True)
    try:
        r = requests.post(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[X728] Chyba API: {r.status_code} {r.text}", flush=True)
    except Exception as e:
        print(f"[X728] Chyba API: {e}", flush=True)

# ---------------- I2C ----------------

def read_voltage(bus):
    data = bus.read_i2c_block_data(MAX17040_ADDR, VOLTAGE_REG, 2)
    raw = (data[0] << 8) | data[1]
    voltage = raw * 1.25 / 1000 / 16
    return round(voltage, 2)

# ---------------- MAIN ----------------

def main():
    print("[X728] Startuji manager (MQTT verze)...", flush=True)

    mqtt_client = mqtt_connect()
    bus = SMBus(I2C_BUS)

    configs = {
        PIN_BUTTON: gpiod.LineSettings(direction=Direction.INPUT, edge_detection=Edge.BOTH),
        PIN_POWERLOSS: gpiod.LineSettings(direction=Direction.INPUT, edge_detection=Edge.BOTH),
        PIN_ENABLE: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE)
    }

    last_check = 0
    last_print = 0
    shutdown_sent = False
    last_power_state = None
    low_voltage_counter = 0

    with gpiod.request_lines(f"/dev/gpiochip{CHIP_ID}", consumer="x728-manager", config=configs) as lines:

        print(f"[X728] GPIO{PIN_ENABLE} = ACTIVE", flush=True)

        while True:
            now = time.time()

            # ----- I2C (baterie) -----
            if now - last_check > CHECK_INTERVAL:
                last_check = now
                try:
                    voltage = read_voltage(bus)

                    # ignoruj nesmysly (0.0 apod.)
                    if voltage < MIN_VALID_VOLTAGE:
                        print(f"[X728] Ignoruji chybne mereni: {voltage} V", flush=True)
                        continue

                    mqtt_client.publish(f"{MQTT_TOPIC_BASE}/battery_voltage", voltage, retain=True)

                    if now - last_print > PRINT_CHECK_INTERVAL:
                        print(f"[X728] Napeti baterie: {voltage} V", flush=True)
                        last_print = now

                    if voltage <= LOW_VOLTAGE:
                        low_voltage_counter += 1
                        print(f"[X728] Nizke napeti {voltage} V ({low_voltage_counter}/{LOW_VOLTAGE_COUNT_LIMIT})", flush=True)
                    else:
                        low_voltage_counter = 0

                    if low_voltage_counter >= LOW_VOLTAGE_COUNT_LIMIT and not shutdown_sent:
                        print("[X728] Potvrzene nizke napeti -> SHUTDOWN", flush=True)
                        mqtt_client.publish(f"{MQTT_TOPIC_BASE}/event", "low_battery_shutdown", retain=True)
                        run_command("shutdown")
                        shutdown_sent = True

                except Exception as e:
                    print(f"[X728] I2C chyba: {e}", flush=True)

            # ----- POWER LOSS (GPIO6) -----
            power_state = lines.get_value(PIN_POWERLOSS)
            if power_state != last_power_state:
                last_power_state = power_state
                if power_state == Value.ACTIVE:
                    print("[X728] POWER LOSS detected (GPIO6=HIGH)", flush=True)
                    mqtt_client.publish(f"{MQTT_TOPIC_BASE}/power_loss", "1", retain=True)
                else:
                    print("[X728] External power restored", flush=True)
                    mqtt_client.publish(f"{MQTT_TOPIC_BASE}/power_loss", "0", retain=True)

            # ----- BUTTON -----
            if lines.wait_edge_events(timeout=0.5):
                for event in lines.read_edge_events():
                    if event.line_offset == PIN_BUTTON and event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                        start_time = time.time()
                        print("[X728] Pin 5 -> HIGH", flush=True)
                        mqtt_client.publish(f"{MQTT_TOPIC_BASE}/button", "pressed")

                        while True:
                            val = lines.get_value(PIN_BUTTON)
                            elapsed = time.time() - start_time

                            if elapsed > SHUTDOWN_MIN and not shutdown_sent:
                                print("[X728] Dlouhy stisk -> SHUTDOWN", flush=True)
                                mqtt_client.publish(f"{MQTT_TOPIC_BASE}/event", "long_press_shutdown", retain=True)
                                run_command("shutdown")
                                shutdown_sent = True

                            if val == Value.INACTIVE:
                                print(f"[X728] Pin 5 -> LOW ({elapsed:.2f}s)", flush=True)
                                if REBOOT_MIN <= elapsed <= REBOOT_MAX:
                                    mqtt_client.publish(f"{MQTT_TOPIC_BASE}/event", "short_press_reboot", retain=True)
                                    run_command("reboot")
                                mqtt_client.publish(f"{MQTT_TOPIC_BASE}/button", "released")
                                break

                            time.sleep(0.05)

            time.sleep(0.1)

if __name__ == "__main__":
    main()