from machine import Pin

motor = Pin(16, Pin.OUT)
motor.value(0)  # start OFF

print("Type 'on' or 'off' to control the motor")

while True:
    cmd = input(">> ").strip().lower()

    if cmd == "on":
        motor.value(1)
        print("Motor ON")

    elif cmd == "off":
        motor.value(0)
        print("Motor OFF")

    else:
        print("Invalid command (use 'on' or 'off')")