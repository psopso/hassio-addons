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

            while True:
                if lines.wait_edge_events(timeout=None):
                    for event in lines.read_edge_events():
                        
                        # Tlacitko stisknuto (nebo zacatek 50s pulzu)
                        if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                            start_time = time.time()
                            print("[X728] Pin 5 -> HIGH", flush=True)
                        
                        # Tlacitko pusteno (nebo konec 50s pulzu)
                        elif event.event_type == gpiod.EdgeEvent.Type.FALLING_EDGE:
                            if start_time == 0: continue
                            
                            duration = time.time() - start_time
                            print(f"[X728] Pin 5 -> LOW (trvani: {duration:.2f}s)", flush=True)

                            # Logika rozhodovani
                            if REBOOT_MIN <= duration <= REBOOT_MAX:
                                print("[X728] Detekovan kratky stisk -> REBOOT", flush=True)
                                run_command("reboot")
                                # Neukoncujeme skript hned, aby deska citila PIN_ENABLE az do konce
                            
                            elif duration > SHUTDOWN_MIN:
                                print(f"[X728] Detekovan dlouhy pulz ({duration:.1f}s) -> SHUTDOWN", flush=True)
                                run_command("shutdown")

                time.sleep(0.01)

    except Exception as e:
        print(f"[X728] KRITICKA CHYBA: {e}", flush=True)

if __name__ == "__main__":
    main()