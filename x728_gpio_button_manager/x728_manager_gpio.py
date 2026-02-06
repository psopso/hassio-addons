import gpiod
from gpiod.line import Direction, Edge, Value
import time
import sys
import requests
from smbus2 import SMBus

# --- KONFIGURACE ---
CHIP_ID = 0
PIN_BUTTON = 5
PIN_ENABLE = 12

REBOOT_MIN = 0.2
REBOOT_MAX = 0.6
SHUTDOWN_MIN = 0.6

I2C_BUS = 1
MAX17040_ADDR = 0x36
VOLTAGE_REG = 0x02
LOW_VOLTAGE = 3.2       # hranice vypnutí
CHECK_INTERVAL = 10    # sekundy

token = sys.argv[1]

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
            print(f"[X728] Chyba Supervisor API: {r.status_code} {r.text}", flush=True)
    except Exception as e:
        print(f"[X728] Chyba API: {e}", flush=True)

def read_voltage(bus):
    data = bus.read_i2c_block_data(MAX17040_ADDR, VOLTAGE_REG, 2)
    raw = (data[0] << 8) | data[1]
    voltage = raw * 1.25 / 1000 / 16
    return round(voltage, 2)

def main():
    print(f"[X728] Startuji manager...", flush=True)

    bus = SMBus(I2C_BUS)

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
    shutdown_sent = False

    with gpiod.request_lines(
        f"/dev/gpiochip{CHIP_ID}",
        consumer="x728-manager",
        config=configs
    ) as lines:

        print(f"[X728] GPIO{PIN_ENABLE} = ACTIVE", flush=True)

        while True:

            # ---- I2C hlídání baterie ----
            now = time.time()
            if now - last_check > CHECK_INTERVAL:
                last_check = now
                try:
                    voltage = read_voltage(bus)
                    #print(f"[X728] Napeti baterie: {voltage} V", flush=True)

                    if voltage <= LOW_VOLTAGE and not shutdown_sent:
                        print("[X728] Nizke napeti -> SHUTDOWN", flush=True)
                        #lines.set_value(PIN_ENABLE, Value.INACTIVE)
                        run_command("shutdown")
                        shutdown_sent = True
                except Exception as e:
                    print(f"[X728] I2C chyba: {e}", flush=True)

            # ---- GPIO tlačítko ----
            if lines.wait_edge_events(timeout=0.5):
                for event in lines.read_edge_events():

                    if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                        start_time = time.time()
                        print("[X728] Pin 5 -> HIGH", flush=True)

                        while True:
                            val = lines.get_value(PIN_BUTTON)
                            elapsed = time.time() - start_time

                            if elapsed > SHUTDOWN_MIN and not shutdown_sent:
                                print("[X728] Dlouhy stisk -> SHUTDOWN", flush=True)
                                lines.set_value(PIN_ENABLE, Value.INACTIVE)
                                run_command("shutdown")
                                shutdown_sent = True

                            if val == Value.INACTIVE:
                                print(f"[X728] Pin 5 -> LOW ({elapsed:.2f}s)", flush=True)
                                if REBOOT_MIN <= elapsed <= REBOOT_MAX:
                                    run_command("reboot")
                                break

                            time.sleep(0.05)

            time.sleep(0.1)

if __name__ == "__main__":
    main()
