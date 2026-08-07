from machine import Pin, I2C
import time

i2c_configs = [
    # I2C0
    ("I2C0", 0, 0, 1),
    ("I2C0", 0, 4, 5),
    ("I2C0", 0, 8, 9),
    ("I2C0", 0, 12, 13),
    ("I2C0", 0, 16, 17),
    ("I2C0", 0, 20, 21),

    # I2C1
    ("I2C1", 1, 2, 3),
    ("I2C1", 1, 6, 7),
    ("I2C1", 1, 10, 11),
    ("I2C1", 1, 14, 15),
    ("I2C1", 1, 18, 19),
    ("I2C1", 1, 22, 23),
    ("I2C1", 1, 26, 27),
]

print("\n--- SCANNING ALL I2C (NORMAL + REVERSED) ---\n")

for name, bus, sda_pin, scl_pin in i2c_configs:
    
    # Try normal
    try:
        print(f"{name} NORMAL  | SDA=GP{sda_pin}, SCL=GP{scl_pin}")
        i2c = I2C(bus, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)
        devices = i2c.scan()

        if devices:
            print(f"  ✅ FOUND: {[hex(d) for d in devices]}")
        else:
            print("  ❌ None")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

    time.sleep(0.1)

    # Try reversed
    try:
        print(f"{name} REVERSED | SDA=GP{scl_pin}, SCL=GP{sda_pin}")
        i2c = I2C(bus, sda=Pin(scl_pin), scl=Pin(sda_pin), freq=100000)
        devices = i2c.scan()

        if devices:
            print(f"  🔄 FOUND (REVERSED): {[hex(d) for d in devices]}")
        else:
            print("  ❌ None")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

    print()
    time.sleep(0.2)

print("\n--- DONE ---\n")