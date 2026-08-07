from machine import Pin, I2C
from bme680 import BME680_I2C
import time

print("Starting BME680 Test...")

# I2C init
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
time.sleep(0.5)

# Scan
devices = i2c.scan()
print("I2C devices:", [hex(d) for d in devices])

# Init sensors
bme1 = None
bme2 = None

if 0x76 in devices:
    try:
        bme1 = BME680_I2C(i2c, address=0x76)
        print("BME680 @ 0x76 initialized")
    except Exception as e:
        print("BME680 @ 0x76 FAILED:", e)

if 0x77 in devices:
    try:
        bme2 = BME680_I2C(i2c, address=0x77)
        print("BME680 @ 0x77 initialized")
    except Exception as e:
        print("BME680 @ 0x77 FAILED:", e)

print("Starting read loop...\n")

# Loop
while True:

    if bme1:
        try:
            print("76:",
                  bme1.temperature,
                  bme1.pressure,
                  bme1.humidity)
        except Exception as e:
            print("76 ERROR:", e)

    if bme2:
        try:
            print("77:",
                  bme2.temperature,
                  bme2.pressure,
                  bme2.humidity)
        except Exception as e:
            print("77 ERROR:", e)

    print("-----")
    time.sleep(1)