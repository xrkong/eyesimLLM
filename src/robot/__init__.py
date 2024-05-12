import logging
import threading
import time

from eye import *

from src.evaluation.data_collection import DataCollection
from src.utils.constant import (
    CONTROL_EVENT_CHECK_FREQUENCY,
    DATA_COLLECTION_FREQUENCY,
    SAFETY_EVENT_CHECK_FREQUENCY,
)


class EyebotBase:
    def __init__(self, speed: int = 0, angspeed: int = 0):
        self.speed = speed
        self.angspeed = angspeed
        self.img = None
        self.psd_sensor_values = []
        self.data_collection_thread = threading.Thread(target=self.data_collection, args=["test2"])
        self.timer = 0
        self.logger = logging.getLogger(__name__)
        CAMInit(QVGA)

    def to_dict(self):
        """
        return the robot's state as a dictionary for data collection
        """
        return {
            "speed": self.speed,
            "angspeed": self.angspeed,
            "img": self.img,
            "psd_sensor_values": self.psd_sensor_values,
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

    def data_collection(self, task_name: str):
        """
        collecting data during the robot's operation
        """
        data_collection = DataCollection()
        self.logger.info("Data collection started!")
        while True:

            self.logger.info(self.psd_sensor_values)
            data_collection.save_data(task_name, self.to_dict())
            time.sleep(DATA_COLLECTION_FREQUENCY)
            self.timer += DATA_COLLECTION_FREQUENCY


