import smbus2
import time
import os
import socket
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

class YahboomHAT:
    ADDRESS = 0x0d
    def __init__(self, bus_n=1):
        self.bus = smbus2.SMBus(bus_n)
    def set_fan(self, speed):
        try: self.bus.write_byte_data(self.ADDRESS, 0x08, max(0, min(9, int(speed))))
        except: pass
    def set_rgb_off(self):
        try: self.bus.write_byte_data(self.ADDRESS, 0x00, 0x00)
        except: pass

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read()) / 1000.0
    except: return 0.0

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "127.0.0.1"

# --- INICIALIZACE OLED (Luma s opravou pro 128x32) ---
try:
    serial = i2c(port=1, address=0x3C)
    # VYNUCENÍ ROZLIŠENÍ 128x32
    # Yahboom HAT někdy vyžaduje rotate=2 (otočení o 180°), pokud je obraz vzhůru nohama
    device = ssd1306(serial, width=128, height=32, rotate=0)
    font = ImageFont.load_default()
    oled_ready = True
    print("OLED inicializován (128x32)")
except Exception as e:
    print(f"OLED Error: {e}")
    oled_ready = False

def update_display(temp, fan_speed):
    if not oled_ready: return
    try:
        with canvas(device) as draw:
            # Vykreslení textu pro 32px výšku (méně řádků, větší přehlednost)
            draw.text((0, 0),  f"IP: {get_ip()}", font=font, fill="white")
            draw.text((0, 11), f"Temp: {temp:.1f} C", font=font, fill="white")
            draw.text((0, 22), f"Fan Speed: {fan_speed}/9", font=font, fill="white")
            
            print(f"Temp: {temp:.1f} C");
            print(f"Fan Speed: {fan_speed}/9");
    except Exception as e:
        print(f"Display update error: {e}")

if __name__ == "__main__":
    hat = YahboomHAT()
    print("Spouštím Yahboom kontroler...")
    
    while True:
        t = get_cpu_temp()
        f_speed = 0
        if t >= 50: f_speed = 9
        elif t >= 45: f_speed = 5
        elif t >= 40: f_speed = 2
        
        hat.set_fan(f_speed)
        update_display(t, f_speed)
        time.sleep(5)
        