# ==========================================
# BOOT SUPERVISOR
# ==========================================

import time
import science as science

print("\n=== PICO BOOT SUPERVISOR ===")

while True:
    try:
        science.run()

    except KeyboardInterrupt:
        print("KeyboardInterrupt — restarting science...")
        time.sleep(1)

    except Exception as e:
        #print("Science crash:", e)
        time.sleep(2)

## manipulator later