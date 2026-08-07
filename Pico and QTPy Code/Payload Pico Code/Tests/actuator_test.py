# =====================================
# ACTUATOR ONLY TEST
# GPIO 7
# =====================================

from machine import Pin, PWM
import time

# Setup PWM on GPIO 7
actuator = PWM(Pin(4))
actuator.freq(50)  # 50Hz servo frequency

print("Actuator Test Starting...")

while True:

    print("Retract")
    actuator.duty_u16(4915)   # ~1ms pulse
    time.sleep(3)

    print("Neutral")
    actuator.duty_u16(8192)   # ~1.5ms pulse
    time.sleep(3)

    print("Extend")
    actuator.duty_u16(11469)  # ~2ms pulse
    time.sleep(3)