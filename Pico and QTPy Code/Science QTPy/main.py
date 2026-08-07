from machine import Pin, I2C, WDT
import onewire
import ds18x20
import time
import sys
import select

# -------------------------
# WATCHDOG TIMER
# -------------------------
wdt = WDT(timeout=8000)

# -------------------------
# ACTUATOR SETUP
# -------------------------

IN1 = Pin(4, Pin.OUT)
IN2 = Pin(6, Pin.OUT)
EN1 = Pin(5, Pin.OUT)

def stop():
    EN1.value(0)
    IN1.value(0)
    IN2.value(0)

def retract():
    EN1.value(1)
    IN1.value(1)
    IN2.value(0)

def extend():
    EN1.value(1)
    IN1.value(0)
    IN2.value(1)

stop()

# -------------------------
# Soil Moisture Sensor (I2C1)
# -------------------------

i2c = I2C(1, sda=Pin(22), scl=Pin(23), freq=100000)
soil_addr = 0x28

try:
    i2c.scan()
except:
    pass

# -------------------------
# DS18B20 Temperature
# -------------------------

dat = Pin(26)
ow = onewire.OneWire(dat)
ds = ds18x20.DS18X20(ow)

try:
    roms = ds.scan()
except:
    roms = []

# -------------------------
# Non-blocking serial check
# -------------------------

def read_command():
    try:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.readline().strip()
    except:
        pass
    return None

# -------------------------
# Main loop
# -------------------------

while True:
    wdt.feed()

    # ---- Check for command ----
    cmd = read_command()
    if cmd:
        print("CMD:", cmd)
        if cmd == "extend":
            extend()
        elif cmd == "retract":
            retract()
        elif cmd == "stop":
            stop()
        else:
            print("Unknown command")

    # ---- Temperature ----
    temp = 0
    try:
        ds.convert_temp()
        for _ in range(10):
            wdt.feed()
            time.sleep_ms(100)
        for rom in roms:
            temp = round(ds.read_temp(rom), 2)
    except:
        pass

    # ---- Moisture ----
    moisture = 0
    try:
        data = i2c.readfrom_mem(soil_addr, 0x05, 2)
        moisture = data[1] << 8 | data[0]
    except:
        pass

    # ---- Print (always same format) ----
    print(f"{moisture}, {temp}")

    wdt.feed()
    time.sleep_ms(900)