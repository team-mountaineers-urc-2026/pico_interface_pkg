# ==========================================
# SCIENCE MODULE (FINAL STABLE) Combo Science Works with topic echoing on ros
# ==========================================

import machine
from machine import Pin, I2C, PWM, WDT
from bme680 import BME680_I2C
import time
import sys
import select


# ==========================================
# INITIALIZATION
# ==========================================

def init():

    # WATCHDOG
    wdt = WDT(timeout=8000)

    # I2C SETUP (with proper delay + scan)
    try:
        i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
        time.sleep(0.3)

        # Retry scan (handles slow sensor boot)
        devices = []
        for _ in range(5):
            devices = i2c.scan()
            if devices:
                break
            time.sleep(0.2)

    except:
        i2c = None
        devices = []

    # SENSOR INIT (only if detected)
    bme1 = None
    bme2 = None

    if i2c:
        if 0x76 in devices:
            try:
                bme1 = BME680_I2C(i2c, address=0x76)
            except:
                bme1 = None

        if 0x77 in devices:
            try:
                bme2 = BME680_I2C(i2c, address=0x77)
            except:
                bme2 = None

    # RELAYS
    halogen = Pin(21, Pin.OUT)
    halogen.value(0)

    vibration = Pin(22, Pin.OUT)   
    vibration.value(0)             

    # LIMIT SWITCHES
    limit_switch_1 = Pin(14, Pin.IN, Pin.PULL_UP)
    limit_switch_2 = Pin(15, Pin.IN, Pin.PULL_UP)

    # ACTUATOR PWM
    actuator_pwm = PWM(Pin(4))
    actuator_pwm.freq(50)
    actuator_pwm.duty_u16(int(65535 * 0.075))  # neutral

    # COMMAND INPUT
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    return {
        "bme1": bme1,
        "bme2": bme2,
        "halogen": halogen,
        "vibration": vibration,
        "actuator_pwm": actuator_pwm,
        "limit_switch_1": limit_switch_1,
        "limit_switch_2": limit_switch_2,
        "poller": poller,
        "wdt": wdt
    }


# ==========================================
# SAFE SENSOR READ
# ==========================================

def read_bme(sensor):
    if sensor:
        try:
            time.sleep(0.05)
            return (
                sensor.temperature,
                sensor.pressure,
                sensor.humidity
            )
        except Exception as e:
            print(f"BME read error: {e}")
            return (0.0, 0.0, 0.0)
    return (0.0, 0.0, 0.0)


# ==========================================
# MAIN LOOP
# ==========================================

def run():

    state = init()

    bme1 = state["bme1"]
    bme2 = state["bme2"]
    halogen = state["halogen"]
    vibration = state["vibration"]
    actuator = state["actuator_pwm"]
    limit_switch_1 = state["limit_switch_1"]
    limit_switch_2 = state["limit_switch_2"]
    poller = state["poller"]
    wdt = state["wdt"]

    STREAM_INTERVAL_MS = 100
    last_stream = time.ticks_ms()

    while True:

        wdt.feed()

        # ---- STREAM ----
        if time.ticks_diff(time.ticks_ms(), last_stream) >= STREAM_INTERVAL_MS:

            t1, p1, h1 = read_bme(bme1)
            t2, p2, h2 = read_bme(bme2)

            lim1 = 0 if limit_switch_1.value() else 1
            lim2 = 0 if limit_switch_2.value() else 1

            print("{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{},{}".format(
                t1, p1, h1,
                t2, p2, h2,
                lim1, lim2
            ))

            last_stream = time.ticks_ms()

        # ---- COMMANDS ----
        if poller.poll(0):
            cmd = sys.stdin.readline().strip()

            if cmd == "hbon":
                halogen.value(1)

            elif cmd == "hboff":
                halogen.value(0)
           
            elif cmd == "vibon":
                vibration.value(1)

            elif cmd == "viboff":
                vibration.value(0)

            elif cmd == "reset":
                machine.reset()

            elif cmd == "act_extend":
                actuator.duty_u16(int(65535 * 0.10))

            elif cmd == "act_retract":
                actuator.duty_u16(int(65535 * 0.05))

            elif cmd == "act_stop":
                actuator.duty_u16(int(65535 * 0.075))

        time.sleep(0.01)


while True:
    try:
        run()
    except Exception as e:
        print(f"Crashed: {e}")
        time.sleep(1)