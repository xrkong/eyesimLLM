import logging
import threading
import time
from typing import Dict, List

import pandas as pd
import pygame
from eye import *
from pygame.locals import *
from src.discrete_movement_robot.action import Action

from src.utils.constant import (
    CONTROL_EVENT_CHECK_FREQUENCY,
    DATA_COLLECTION_FREQUENCY,
    DATA_DIR,
    SAFETY_EVENT_CHECK_FREQUENCY,
)
from src.utils.utils import cam2image, encode_image, lidar2image, save_item_to_csv


class DiscreteMovementEyebot:
    def __init__(self, task_name: str):
        self.logger = logging.getLogger(__name__)
        self.task_name = task_name
        CAMInit(QVGA)
        self.img = CAMGet()
        self.scan = LIDARGet()
        self.x = 0
        self.y = 0
        self.phi = 0
        self.step = 1
        self.img_dir = DATA_DIR / self.task_name / "images"
        self.img_dir.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / self.task_name).mkdir(parents=True, exist_ok=True)
        self.file_path = f"{DATA_DIR}/{self.task_name}/robot_state.csv"
        self.last_command = ""

    def to_dict(self) -> Dict:
        """
        return the robot's state as a dictionary for data collection
        """
        img_path = f"{self.img_dir}/{self.step}.png"
        lidar_path = f"{self.img_dir}/{self.step}_lidar.png"
        return {
            "step": self.step,
            "x": self.x,
            "y": self.y,
            "phi": self.phi,
            "img_path": img_path,
            "lidar_path": lidar_path,
        }

    def get_current_state(self, camera=True) -> Dict:
        """
        Get the current state of the robot
        """
        state = self.to_dict()
        lidar_base64 = encode_image(state["lidar_path"])
        imgs = [lidar_base64]
        if camera:
            img_base64 = encode_image(state["img_path"])
            imgs = [img_base64, lidar_base64]
        last_command = (
            None
            if not self.last_command
            else [action.to_str() for action in self.last_command]
        )
        return {
            "position": {
                "x": state["x"],
                "y": state["y"],
                "phi": state["phi"],
            },
            "last_command": last_command,
            "images": imgs,
        }

    def straight(self, distance: int, speed: int, direction: str):
        """
        move the robot straight for a given distance
        """
        factor = 1 if direction == "forward" else -1
        VWStraight(factor * distance, speed)
        VWWait()
        self.update_state()

    def turn(self, angle: int, speed: int, direction: str):
        """
        turn the robot for a given angle
        """
        factor = 1 if direction == "left" else -1
        VWTurn(factor * angle, speed)
        VWWait()
        self.update_state()

    def update_sensors(self):
        """
        update the robot's camera and lidar
        """
        self.img = CAMGet()
        LCDImage(self.img)
        self.scan = LIDARGet()

    def update_state(self):
        """
        update the robot's state with the given speed and angspeed
        """
        self.x, self.y, self.phi = VWGetPosition()

    def run(self, security: bool = False):
        raise NotImplementedError

    def data_collection(self):
        """
        collecting data during the robot's operation
        """
        self.logger.info("Data collection started!")
        current_state = self.to_dict()
        cam2image(self.img).save(current_state["img_path"])
        lidar2image(scan=list(self.scan), save_path=current_state["lidar_path"])
        save_item_to_csv(item=current_state, file_path=self.file_path)

    def load_data_from_csv(self):
        """
        load the data from the csv file
        """
        return pd.read_csv(f"{DATA_DIR}/{self.task_name}.csv")
