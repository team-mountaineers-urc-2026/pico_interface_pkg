from machine import Pin
import time

IN1 = Pin(4, Pin.OUT)   # GPIO4
IN2 = Pin(6, Pin.OUT)   # GPIO6
EN1 = Pin(5, Pin.OUT)   # GPIO5

# Make sure it starts OFF
EN1.value(0)
IN1.value(0)
IN2.value(0)

def stop():
    EN1.value(0)
    IN1.value(0)
    IN2.value(0)

def extend():
    EN1.value(1)
    IN1.value(1)
    IN2.value(0)

def retract():
    EN1.value(1)
    IN1.value(0)
    IN2.value(1)

while True:
    print("Extending")
    extend()
    time.sleep(3)

    print("Stopping")
    stop()
    time.sleep(2)

    print("Retracting")
    retract()
    time.sleep(3)

    print("Stopping")
    stop()
    time.sleep(3)