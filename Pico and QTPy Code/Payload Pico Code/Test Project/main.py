from machine import Pin
import time

IN1 = Pin(20, Pin.OUT, value=0)
IN2 = Pin(19, Pin.OUT, value=0)

time.sleep(2)

# Try direction 1
IN1.value(1)
IN2.value(0)
time.sleep(3)

# Stop
IN1.value(0)
IN2.value(0)
time.sleep(2)

# Try direction 2
IN1.value(0)
IN2.value(1)
time.sleep(3)

# Stop
IN1.value(0)
IN2.value(0)