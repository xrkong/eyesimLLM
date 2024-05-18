import csv
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
    IMAGE_DIR,
    SAFETY_EVENT_CHECK_FREQUENCY,
)
from src.utils.utils import cam2image, lidar2image


class EyebotBase:
    def __init__(self, task_name:str, speed: int = 0, angspeed: int = 0):
        self.task_name = task_name
        self.speed = speed
        self.angspeed = angspeed
        self.img = None
        self.psd_values = {"front": 0, "left": 0, "right": 0, "back": 0}
        self.scan = None
        self.experiment_time = 0
        self.logger = logging.getLogger(__name__)
        self.safety_event = threading.Event()
        (IMAGE_DIR / self.task_name).mkdir(parents=True, exist_ok=True)
        self.data_collection_thread = threading.Thread(target=self.data_collection)

        CAMInit(QVGA)

    def to_dict(self):
        """
        return the robot's state as a dictionary for data collection
        """
        img_path = f'{IMAGE_DIR}/{self.task_name}/{self.experiment_time}.png'
        lidar_path = f'{IMAGE_DIR}/{self.task_name}/{self.experiment_time}_lidar.png'
        return {
            "experiment_time": self.experiment_time,
            "speed": self.speed,
            "angspeed": self.angspeed,
            "img_path": img_path,
            "lidar_path": lidar_path,
            # "psd_front": self.psd_values["front"],
            # "psd_left": self.psd_values["left"],
            # "psd_right": self.psd_values["right"],
            # "psd_back": self.psd_values["back"],
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

    def safety_check(self):
        """
        check the safety of the robot
        """
        while True:
            # TODO: implement safety mechanism
            self.img = CAMGet()
            LCDImage(self.img)
            self.scan = LIDARGet()
            # self.psd_values["front"] = PSDGet(PSD_FRONT)
            # self.psd_values["left"] = PSDGet(PSD_LEFT)
            # self.psd_values["right"] = PSDGet(PSD_RIGHT)
            # self.psd_values["back"] = PSDGet(PSD_BACK)
            if any(value < 300 for key, value in self.psd_values.items()):
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
            if self.speed != 0 or self.angspeed != 0:
                file_path = f'{DATA_DIR}/{self.task_name}.csv'
                current_state = self.to_dict()
                fieldnames = current_state.keys()
                # save the image
                cam2image(self.img).save(current_state["img_path"])
                lidar2image(scan=list(self.scan), experiment_time=str(current_state['experiment_time']), save_path=current_state["lidar_path"])
                # save the data
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    # Write headers only if the file is empty
                    if file.tell() == 0:
                        writer.writeheader()
                    writer.writerow(current_state)
            time.sleep(DATA_COLLECTION_FREQUENCY)
            self.experiment_time += DATA_COLLECTION_FREQUENCY

    def load_data_from_csv(self):
        """
        load the data from the csv file
        """
        return pd.read_csv(f'{DATA_DIR}/{self.task_name}.csv')
