# ==========================================
# PICO SCIENCE FAKE SENSOR EMULATOR
# ==========================================

import time
import math
import random
import machine
from machine import Pin, PWM
import sys
import select

print("=== FAKE SCIENCE SENSOR MODE ===")

# ----------------------------
# RELAYS (still functional)
# ----------------------------
halogen = Pin(21, Pin.OUT)
halogen.value(0)

u2d2 = Pin(22, Pin.OUT)
u2d2.value(1)

# ----------------------------
# ACTUATOR
# ----------------------------
actuator_pwm = PWM(Pin(7))
actuator_pwm.freq(50)
actuator_pwm.duty_u16(int(65535 * 0.075))

# ----------------------------
# NONBLOCKING INPUT
# ----------------------------
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

start_time = time.ticks_ms()

while True:

    t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

    # ----------------------------
    # SENSOR 1 (INSIDE ROVER)
    # ----------------------------
    t1 = 31.5 + 0.5 * math.sin(t / 10)
    p1 = 101.8 + 0.1 * math.sin(t / 20)
    h1 = 40 + 5 * math.sin(t / 15)

    # ----------------------------
    # SENSOR 2 (OUTSIDE ROOM)
    # ----------------------------
    t2 = 22.5 + 0.5 * math.sin(t / 8)
    p2 = 101.3 + 0.1 * math.sin(t / 18)
    h2 = 50 + 5 * math.sin(t / 12)

    print("{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}".format(
        t1, p1, h1, t2, p2, h2
    ))

    # ----------------------------
    # COMMAND HANDLING
    # ----------------------------
    if poller.poll(0):
        cmd = sys.stdin.readline().strip()

        if cmd == "hbon":
            halogen.value(1)

        elif cmd == "hboff":
            halogen.value(0)

        elif cmd == "u2d2on":
            u2d2.value(0)

        elif cmd == "u2d2off":
            u2d2.value(1)

        elif cmd == "act_extend":
            actuator_pwm.duty_u16(int(65535 * 0.10))

        elif cmd == "act_retract":
            actuator_pwm.duty_u16(int(65535 * 0.05))

        elif cmd == "act_stop":
            actuator_pwm.duty_u16(int(65535 * 0.075))

        elif cmd == "reset":
            machine.reset()

    time.sleep(0.2)