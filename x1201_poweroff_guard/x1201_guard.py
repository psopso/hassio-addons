import signal
import time
import gpiod
from gpiod.line import Direction, Value

GPIO_CHIP = "/dev/gpiochip0"
GPIO_AC = 6


def handle_shutdown(signum, frame):
    print("[X1201] SIGTERM received", flush=True)

    try:
        print("[X1201] Trying to acquire GPIO6...", flush=True)

        # GPIO si vezmeme AŽ TEĎ.
        # Za normálního provozu ho vůbec nedržíme.
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

            print(
                f"[X1201] GPIO6 = "
                f"{'HIGH -> AC PRESENT' if value == Value.ACTIVE else 'LOW -> AC ABSENT'}",
                flush=True
            )

            print(
                f"[X1201] timestamp = {time.time()}",
                flush=True
            )

    except Exception as e:
        print(f"[X1201] ERROR acquiring GPIO6: {e}", flush=True)

    print("[X1201] Exiting", flush=True)
    raise SystemExit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

print("[X1201] Guard started", flush=True)

# GPIO6 zde NENÍ otevřené.
# Pouze čekáme na ukončení kontejneru.
while True:
    time.sleep(3600)