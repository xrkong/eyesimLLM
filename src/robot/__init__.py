import csv
import logging
import threading
import time

import pandas as pd
from eye import *

from src.utils.constant import (
    CONTROL_EVENT_CHECK_FREQUENCY,
    DATA_COLLECTION_FREQUENCY,
    DATA_DIR,
    IMAGE_DIR,
    SAFETY_EVENT_CHECK_FREQUENCY,
)


class EyebotBase:
    def __init__(self, task_name:str, speed: int = 0, angspeed: int = 0):
        self.task_name = task_name
        self.speed = speed
        self.angspeed = angspeed
        self.img = None
        self.psd_values = {"front": 0, "left": 0, "right": 0, "back": 0}
        self.timer = 0
        self.logger = logging.getLogger(__name__)

        (IMAGE_DIR / self.task_name).mkdir(parents=True, exist_ok=True)
        self.data_collection_thread = threading.Thread(target=self.data_collection)

        CAMInit(QVGA)

    def to_dict(self):
        """
        return the robot's state as a dictionary for data collection
        """
        img_path = f'{IMAGE_DIR}/{self.task_name}/{self.timer}.jpg'
        return {
            "speed": self.speed,
            "angspeed": self.angspeed,
            "img_path": img_path,
            "psd_front": self.psd_values["front"],
            "psd_left": self.psd_values["left"],
            "psd_right": self.psd_values["right"],
            "psd_back": self.psd_values["back"],
            "timestamp": self.timer
        }

    def move(self, speed, angspeed):
        """
        move the robot with the given speed and angspeed
        """
        self.update_state(speed, angspeed)

    def stop(self):
        """
        stop the robot -> set speed and angspeed to 0
        """
        self.update_state(0, 0)

    def update_state(self, speed, angspeed):
        """
        update the robot's state with the given speed and angspeed
        """
        self.speed = speed
        self.angspeed = angspeed
        VWSetSpeed(self.speed, self.angspeed)

    def data_collection(self):
        """
        collecting data during the robot's operation
        """
        self.logger.info("Data collection started!")
        while True:
            if self.speed != 0 or self.angspeed != 0:
                file_path = f'{DATA_DIR}/{self.task_name}.csv'
                current_state = self.to_dict()
                fieldnames = current_state.keys()
                # save the image
                with open(current_state["img_path"], 'wb') as f:
                    f.write(self.img)
                # save the data
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    # Write headers only if the file is empty
                    if file.tell() == 0:
                        writer.writeheader()
                    writer.writerow(current_state)
            time.sleep(DATA_COLLECTION_FREQUENCY)
            self.timer += DATA_COLLECTION_FREQUENCY

    def load_data_from_csv(self):
        """
        load the data from the csv file
        """
        return pd.read_csv(f'{DATA_DIR}/{self.task_name}.csv')
