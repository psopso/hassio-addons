import signal
import time
import gpiod
from gpiod.line import Direction, Value

from datetime import datetime

CHIP = "/dev/gpiochip0"
GPIO_AC = 6

def shutdown(signum, frame):
    print("[X1201] SIGTERM received", flush=True)

#    value = lines.get_value(GPIO_AC)

#    if value == Value.ACTIVE:
#        print("[X1201] GPIO6 = HIGH -> AC PRESENT", flush=True)
#    else:
#        print("[X1201] GPIO6 = LOW -> AC ABSENT", flush=True)

#    print(f"[X1201] timestamp = {time.time()}", flush=True)
    print(f"[X1201] timestamp = {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}", flush=True)

    # ZATÍM NIC NEDĚLAT
    # pouze ukončit addon
    raise SystemExit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

#with gpiod.request_lines(
#    CHIP,
#    consumer="x1201-poweroff-guard",
#    config={
#        GPIO_AC: gpiod.LineSettings(
#            direction=Direction.INPUT
#        )
#    }
#) as lines:
if True:
    print("[X1201] Guard started", flush=True)

    while True:
        time.sleep(3600)
