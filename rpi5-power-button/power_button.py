#!/usr/bin/env python3
from evdev import InputDevice, ecodes
import os
import requests
import time
import threading
import json

def load_config():
    """Lade Addon-Konfiguration"""
    config_path = "/data/options.json"
    default_config = {
        "long_press_duration": 3.0,
        "long_press_behaviour": "shutdown"
    }
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print(f"Config loaded: {config}", flush=True)
            return config
    except FileNotFoundError:
        print("No config file found, using defaults", flush=True)
        return default_config
    except Exception as e:
        print(f"Error loading config: {e}, using defaults", flush=True)
        return default_config

def send_action_request(token, action):
    """Verschiedene Actions in separatem Thread"""
    urls = {
        "shutdown": "http://supervisor/host/shutdown",
        "reboot": "http://supervisor/host/reboot",
        "reload": "http://supervisor/core/restart"
    }
    
    if action not in urls:
        print(f"Unknown action: {action}", flush=True)
        return
        
    try:
        response = requests.post(
            urls[action],
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=2
        )
        print(f"{action.capitalize()} request completed: {response.status_code}", flush=True)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
        print(f"{action.capitalize()} initiated (expected timeout/connection loss)", flush=True)
    except Exception as e:
        print(f"{action.capitalize()} error: {e}", flush=True)

def send_event(token, event_type, duration, threshold):
    """Event an Home Assistant senden"""
    try:
        response = requests.post(
            f"http://supervisor/core/api/events/power_button",
            json={
                "state": event_type,
                "duration": f"{duration:.2f}",
                "threshold": threshold,
                "button_type": "long_press" if event_type == "long_press" else "short_press"
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=2
        )
        print(f"Event '{event_type}' sent successfully", flush=True)
    except Exception as e:
        print(f"Error sending event: {e}", flush=True)

# Konfiguration laden
config = load_config()
LONG_PRESS_THRESHOLD = config.get("long_press_duration", 3.0)
LONG_PRESS_BEHAVIOUR = config.get("long_press_behaviour", "shutdown").lower()

print(f"Power Button Listener starting:", flush=True)
print(f"  Long press threshold: {LONG_PRESS_THRESHOLD}s", flush=True)
print(f"  Long press behaviour: {LONG_PRESS_BEHAVIOUR}", flush=True)

# Input Device öffnen
INPUT_DEVICE = "/dev/input/event0"
try:
    dev = InputDevice(INPUT_DEVICE)
    print(f"  Input device: {INPUT_DEVICE}", flush=True)
except Exception as e:
    print(f"Cannot open input device {INPUT_DEVICE}: {e}", flush=True)
    exit(1)

token = os.environ.get("SUPERVISOR_TOKEN")
if not token:
    print("ERROR: SUPERVISOR_TOKEN not found!", flush=True)
    exit(1)

press_time = None

print("Listening for Power Button events...")

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_POWER:
        if event.value == 1:  # gedrückt
            press_time = time.monotonic()
            print("Power button pressed", flush=True)
        elif event.value == 0 and press_time:  # losgelassen
            raw_duration = time.monotonic() - press_time
            duration = raw_duration + 0.5
            print(f"Power button released (held for {duration:.2f}s)", flush=True)

            if duration >= LONG_PRESS_THRESHOLD:
                print(f"Long press detected ({duration:.2f}s >= {LONG_PRESS_THRESHOLD}s)", flush=True)
                
                if LONG_PRESS_BEHAVIOUR == "none":
                    print("Long press behaviour: none - sending event", flush=True)
                    send_event(token, "long_press", duration, LONG_PRESS_THRESHOLD)
                elif LONG_PRESS_BEHAVIOUR in ["shutdown", "reboot", "reload"]:
                    print(f"Long press behaviour: {LONG_PRESS_BEHAVIOUR}", flush=True)
                    
                    # Action in separatem Thread ausführen
                    action_thread = threading.Thread(
                        target=send_action_request, 
                        args=(token, LONG_PRESS_BEHAVIOUR)
                    )
                    action_thread.daemon = True
                    action_thread.start()
                    
                    if LONG_PRESS_BEHAVIOUR != "reload":
                        # Bei shutdown/reboot Script beenden
                        time.sleep(1)
                        break
                else:
                    print(f"Unknown long press behaviour: {LONG_PRESS_BEHAVIOUR}", flush=True)
                    send_event(token, "long_press", duration, LONG_PRESS_THRESHOLD)
                    
            else:
                print(f"Short press detected ({duration:.2f}s < {LONG_PRESS_THRESHOLD}s)", flush=True)
                send_event(token, "short_press", duration, LONG_PRESS_THRESHOLD)
            
            press_time = None

print("Power Button Listener stopped", flush=True)