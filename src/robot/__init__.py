import logging
import threading
import time
from typing import Dict, List

import pandas as pd
import pygame
from eye import *
from pygame.locals import *

from src.utils.constant import (
    CONTROL_EVENT_CHECK_FREQUENCY,
    DATA_COLLECTION_FREQUENCY,
    DATA_DIR,
    SAFETY_EVENT_CHECK_FREQUENCY,
)
from src.utils.utils import cam2image, encode_image, lidar2image, save_item_to_csv


class EyebotBase:
    def __init__(self, task_name: str):

        """
        Initialize the EyebotBase class
        Args:
        task_name (str): the name of the task
        speed (int): the speed of the robot
        angspeed (int): the angular speed of the robot
        img (numpy array): the image from the camera
        scan (numpy array): the lidar scan data
        experiment_time (int): the time of the experiment
        logger (logging.Logger): the logger object
        safety_event (threading.Event): the safety event
        data_collection_thread (threading.Thread): the data collection thread
        file_path (str): the file path for saving the data
        lock (threading.Lock): the lock object
        """

        self.task_name = task_name
        self.speed = 0
        self.angspeed = 0
        CAMInit(QVGA)
        self.img = CAMGet()
        self.scan = LIDARGet()
        self.experiment_time = 0
        self.logger = logging.getLogger(__name__)
        self.safety_event = threading.Event()
        self.img_dir = DATA_DIR / self.task_name / "images"
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = f"{DATA_DIR}/{self.task_name}.csv"
        self.data_collection_thread = threading.Thread(target=self.data_collection)
        self.lock = threading.Lock()

    def to_dict(self):
        """
        return the robot's state as a dictionary for data collection
        """
        img_path = f"{self.img_dir}/{self.experiment_time}.png"
        lidar_path = f"{self.img_dir}/{self.experiment_time}_lidar.png"
        return {
            "experiment_time": self.experiment_time,
            "speed": self.speed,
            "angspeed": self.angspeed,
            "img_path": img_path,
            "lidar_path": lidar_path,
            "safety_event": self.safety_event.is_set(),
        }

    def get_current_state(self):
        """
        Get the current state of the robot
        """
        state = self.to_dict()
        img_base64 = encode_image(state["img_path"])
        lidar_base64 = encode_image(state["lidar_path"])
        return {
            "text": {
                "speed": state["speed"],
                "angspeed": state["angspeed"],
            },
            "images": [img_base64, lidar_base64],
        }

    def move(self, speed, angspeed):
        """
        move the robot with the given speed and angspeed
        """
        self.update_state(speed, angspeed)

    def update_state(self, speed, angspeed):
        """
        update the robot's state with the given speed and angspeed
        """
        self.speed = speed
        self.angspeed = angspeed
        VWSetSpeed(self.speed, self.angspeed)

    def manual_control(self):
        """
        control the robot manually
        """
        max_speed = 300
        min_speed = -300
        speed_increment = 25
        max_steer = 90
        min_steer = -90
        steer_increment = 5

        pygame.time.Clock().tick(30)
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            self.speed = self.speed + speed_increment
        if keys[K_s]:
            self.speed = self.speed - speed_increment
        if keys[K_a]:
            self.angspeed = self.angspeed + steer_increment
        if keys[K_d]:
            self.angspeed = self.angspeed - steer_increment

        if self.speed < min_speed:
            self.speed = min_speed
        elif self.speed > max_speed:
            self.speed = max_speed

        if self.angspeed < min_steer:
            self.angspeed = min_steer
        elif self.angspeed > max_steer:
            self.angspeed = max_steer

        if not (keys[K_a] or keys[K_d]):
            self.angspeed = 0

        self.move(self.speed, self.angspeed)

    def emergency_stop(self, range_degrees=30):
        """
        Check if the robot needs to stop based on its speed and lidar data.
        Returns:
        bool: True if the robot needs to stop, False otherwise.
        """
        # for checking the front
        offset = 179
        if self.speed < 0:
            # for checking the back
            offset = 0

        # Calculate the safe stopping distance as twice the current speed
        safe_stopping_distance = 3 * abs(self.speed)
        degrees = []
        # Check distances in the range around the current direction
        for direction_to_check in range(-range_degrees, range_degrees + 1):
            distance_in_direction = self.scan[offset + direction_to_check]
            degrees.append((direction_to_check, distance_in_direction))
            if (
                distance_in_direction < safe_stopping_distance
                or distance_in_direction < 200
            ):
                return True
        # self.logger.info(degrees)
        return False

    def safety_check(self):
        """
        check the safety of the robot
        """
        while True:
            self.img = CAMGet()
            LCDImage(self.img)
            self.scan = LIDARGet()
            if self.emergency_stop():
                self.safety_event.set()
            time.sleep(SAFETY_EVENT_CHECK_FREQUENCY)

    def run(self):
        raise NotImplementedError

    def data_collection(self):
        """
        collecting data during the robot's operation
        """
        self.logger.info("Data collection started!")
        while True:
            current_state = self.to_dict()
            fieldnames = current_state.keys()
            # save the image
            with self.lock:
                cam2image(self.img).save(current_state["img_path"])
                lidar2image(scan=list(self.scan), save_path=current_state["lidar_path"])
            # save the data
            save_item_to_csv(item=current_state, file_path=self.file_path)
            time.sleep(DATA_COLLECTION_FREQUENCY)
            self.experiment_time += DATA_COLLECTION_FREQUENCY

    def load_data_from_csv(self):
        """
        load the data from the csv file
        """
        return pd.read_csv(f"{DATA_DIR}/{self.task_name}.csv")
