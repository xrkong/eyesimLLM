import threading
import time

from eye import *

condition_event = threading.Event()


def infinite_loop():
    count = 1
    while not condition_event.is_set():
        print(count)
        if count == 5:
            VWSetSpeed(40, 10)
            # condition_event.set()
        if count == 15:
            VWSetSpeed(40, -10)
            count = 0
        time.sleep(1)
        count += 1


if __name__ == "__main__":
    thread = threading.Thread(target=infinite_loop)
    thread.start()
    while True:
        psd_sensor_values = [PSDGet(i) for i in range(1, 7)]
        print(psd_sensor_values)
        if any(value < 200 for value in psd_sensor_values):
            condition_event.set()
            break
        time.sleep(2)

    VWSetSpeed(0, 0)
