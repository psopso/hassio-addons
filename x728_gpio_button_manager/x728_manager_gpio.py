import gpiod
from gpiod.line import Direction, Edge, Value
import time
import subprocess
import sys

import os
import requests

# --- KONFIGURACE ---
CHIP_ID = 0
PIN_BUTTON = 5    # Vstup od tlacitka
PIN_ENABLE = 12   # Boot OK / Power Management pin

REBOOT_MIN = 0.2  # Minimální délka pro reboot
REBOOT_MAX = 0.6  # Maximální délka pro reboot (pokrývá vašich 500ms)
SHUTDOWN_MIN = 0.6 # Pulz delší než 3s (vašich 50s v "active" stavu)

token = sys.argv[1]

def run_command(action):
    url = f"http://supervisor/host/{action}"
    #token = os.environ.get("SUPERVISOR_TOKEN")

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
        print(f"[X728] Chyba pri volani Supervisor API: {e}", flush=True)
'''
def run_command(action):
    """Volání Bashio pro ovládání hostitele"""
    # Bashio příkazy se v HA add-onech spouštějí takto:
    cmd = ["bashio", f"host.{action}"]
    try:
        print(f"[X728] Executing {action} via Bashio...")
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Chyba při komunikaci s Bashio: {e}")
'''

def main():
    print(f"[X728] Startuji manager na chipu {CHIP_ID}...", flush=True)

    # Definice nastavení pro oba piny
    configs = {
        PIN_BUTTON: gpiod.LineSettings(
            direction=Direction.INPUT,
            edge_detection=Edge.BOTH
        ),
        PIN_ENABLE: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.ACTIVE  # Nastavi GPIO12 na 1 (Active)
        )
    }

    try:
        with gpiod.request_lines(
            f"/dev/gpiochip{CHIP_ID}",
            consumer="x728-manager",
            config=configs
        ) as lines:

            print(f"[X728] GPIO{PIN_ENABLE} nastaven na ACTIVE. Cekam na tlacitko...", flush=True)

            start_time = 0
            shutdown_sent = False

            while True:
                if lines.wait_edge_events(timeout=None):
                    for event in lines.read_edge_events():

                        if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                            start_time = time.time()
                            shutdown_sent = False
                            print("[X728] Pin 5 -> HIGH", flush=True)

                            # Aktivně sleduj délku pulzu
                            while True:
                                val = lines.get_value(PIN_BUTTON)
                                elapsed = time.time() - start_time

                                if not shutdown_sent and elapsed > SHUTDOWN_MIN:
                                    print(f"[X728] Dlouhy pulz {elapsed:.1f}s -> SHUTDOWN", flush=True)
                                    print("System bude vypnut za 1 minutu.")
                                    time.sleep(60)
				    lines.setvalue(PIN_ENABLE, Value.INACTIVE)
                                    run_command("shutdown")
                                    shutdown_sent = True

                                if val == Value.INACTIVE:
                                    print(f"[X728] Pin 5 -> LOW (trvani: {elapsed:.2f}s)", flush=True)

                                    if REBOOT_MIN <= elapsed <= REBOOT_MAX:
                                        print("[X728] Kratky stisk -> REBOOT", flush=True)
                                        run_command("reboot")

                                    break

                                time.sleep(0.05)

                time.sleep(0.01)

    except Exception as e:
        print(f"[X728] KRITICKA CHYBA: {e}", flush=True)

if __name__ == "__main__":
    main()