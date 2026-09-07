import signal
import time
from datetime import datetime, timezone

import gpiod
from gpiod.line import Direction, Value


GPIO_CHIP = "/dev/gpiochip0"
GPIO_AC = 6


def log(message):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3]

    print(f"[{timestamp} UTC] [X1201] {message}", flush=True)


def handle_shutdown(signum, frame):
    log("SIGTERM received")
    log("Trying to acquire GPIO6...")

    try:
        with gpiod.request_lines(
            GPIO_CHIP,
            consumer="x1201-poweroff-guard",
            config={
                GPIO_AC: gpiod.LineSettings(
                    direction=Direction.INPUT
                )
            }
        ) as lines:

            value = lines.get_value(GPIO_AC)

            if value == Value.ACTIVE:
                log("GPIO6 = HIGH -> AC PRESENT")
                # Předání informace skriptu finish
                with open("/run/x1201-reboot", "w") as f:
                  f.write("1\n")
            else:
                log("GPIO6 = LOW -> AC ABSENT")

    except Exception as e:
        log(f"ERROR acquiring GPIO6: {e}")

    log("Python exiting")
    raise SystemExit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

log("Guard started")

while True:
    time.sleep(3600)