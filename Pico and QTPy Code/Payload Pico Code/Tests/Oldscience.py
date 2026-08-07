# ==========================================
# SCIENCE MODULE
# ==========================================

import machine
from machine import Pin, I2C, PWM
from bme680 import BME680_I2C
import time
import sys
import select


# ==========================================
# INITIALIZATION
# ==========================================

def init():

    print("Science Init Starting...")

    # I2C
    try:
        i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
        print("I2C Initialized")
    except Exception as e:
        print("I2C ERROR:", e)
        i2c = None

    # Sensors
    bme1 = None
    bme2 = None

    if i2c:
        try:
            bme1 = BME680_I2C(i2c, address=0x76)
            print("BME680 #1 OK")
        except:
            print("BME680 #1 FAIL")

        try:
            bme2 = BME680_I2C(i2c, address=0x77)
            print("BME680 #2 OK")
        except:
            print("BME680 #2 FAIL")

    # Relays
    halogen = Pin(21, Pin.OUT)
    halogen.value(0)

    # Limit Switches
    limit_switch_1 = Pin(14, Pin.IN, Pin.PULL_UP)
    limit_switch_2 = Pin(15, Pin.IN, Pin.PULL_UP)   


    # ------------------------------------------
    # Linear Actuator (PWM on GPIO 7)
    # ------------------------------------------
    actuator_pwm = PWM(Pin(4))
    actuator_pwm.freq(50)
    actuator_pwm.duty_u16(int(65535 * 0.075))  # Neutral
    print("Actuator PWM Initialized")

    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    return {
        "bme1": bme1,
        "bme2": bme2,
        "halogen": halogen,
        "actuator_pwm": actuator_pwm,
        "limit_switch_1": limit_switch_1,
        "limit_switch_2": limit_switch_2,
        "poller": poller
    }


# ==========================================
# SAFE SENSOR READ
# ==========================================

def read_bme(sensor):
    if sensor:
        try:
            return (
                sensor.temperature,
                sensor.pressure,
                sensor.humidity
            )
        except:
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
    actuator = state["actuator_pwm"]
    limit_switch_1 = state["limit_switch_1"]
    limit_switch_2 = state["limit_switch_2"]
    poller = state["poller"]

    print("Science Running...")

    STREAM_INTERVAL_MS = 1000
    last_stream = time.ticks_ms()

    while True:

        # ---- STREAM ----
        if time.ticks_diff(time.ticks_ms(), last_stream) >= STREAM_INTERVAL_MS:

            t1, p1, h1 = read_bme(bme1)
            t2, p2, h2 = read_bme(bme2)
            lim1 = 0 if limit_switch_1.value() else 1
            lim2 = 0 if limit_switch_2.value() else 1

            print("{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{},{}".format(
                t1, p1, h1, t2, p2, h2, lim1, lim2
            ))

            last_stream = time.ticks_ms()

        # ---- COMMANDS ----
        if poller.poll(0):
            cmd = sys.stdin.readline().strip()

            if cmd == "hbon":
                halogen.value(1)

            elif cmd == "hboff":
                halogen.value(0)

            elif cmd == "reset":
                machine.reset()

            elif cmd == "act_extend":
                actuator.duty_u16(int(65535 * 0.10))

            elif cmd == "act_retract":
                actuator.duty_u16(int(65535 * 0.05))

            elif cmd == "act_stop":
                actuator.duty_u16(int(65535 * 0.075))

        time.sleep(0.01)