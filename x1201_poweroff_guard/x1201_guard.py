import signal
import time
from datetime import datetime, timezone

import gpiod
from gpiod.line import Direction, Value


GPIO_CHIP = "/dev/gpiochip0"
GPIO_AC = 6


def log(message):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp} UTC] [X1201] {message}", flush=True)


def handle_shutdown(signum, frame):
    log("SIGTERM received")

    for attempt in range(10):
        try:
            log(f"Trying to acquire GPIO6 (attempt {attempt + 1})...")

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
                else:
                    log("GPIO6 = LOW -> AC ABSENT")

                break

        except Exception as e:
            log(f"GPIO6 busy: {e}")
            time.sleep(0.2)

    else:
        log("Could not acquire GPIO6")

    log("Exiting")
    raise SystemExit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

log("Guard started")

while True:
    time.sleep(3600)