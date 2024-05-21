import csv
import logging
import threading
import time
from typing import Dict, List
import math

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
    def __init__(self, task_name:str):

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
        (IMAGE_DIR / self.task_name).mkdir(parents=True, exist_ok=True)
        self.file_path = f'{DATA_DIR}/{self.task_name}.csv'
        self.data_collection_thread = threading.Thread(target=self.data_collection)



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
            "safety_event": self.safety_event.is_set(),
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
            if distance_in_direction < safe_stopping_distance or distance_in_direction < 200:
                return True
        # self.logger.info(degrees)
        return False
    
    def dog_drive(self, x, y):
        _turn_speed = 50
        _drive_speed = 100
        _cur_x, _cur_y, _cur_heading = VWGetPosition()
        _desired_heading = int(math.degrees(math.atan2(y - _cur_y, x - _cur_x)))
        print(_desired_heading - _cur_heading)
        
        # Turn to face the goal
        # VWTurn(sphi - rphi, _turn_speed)
        # VWSetSpeed(0, -_turn_speed)
        # time.sleep(abs(sphi - rphi)/_turn_speed)
        # VWWait()
        _steer = 0 
        while (d := math.dist((_cur_x, _cur_y), (x, y))) > 100:
            _cur_x, _cur_y, _cur_heading = VWGetPosition()
            _desired_heading = int(math.degrees(math.atan2(y - _cur_y, x - _cur_x)))
            print(_desired_heading - _cur_heading)

            # Edge case to handle discontinuity between +180 and -180
            rotation = _desired_heading - _cur_heading
            if rotation > 180:
                rotation -= 360
            elif rotation < -180:
                rotation += 360

            print("rotation:"+str(rotation)+" desired_heading:"+str(_desired_heading)+" cur_heading:"+str(_cur_heading))
            if _cur_heading > _desired_heading + 10:
                _steer -= 5
            elif _cur_heading < _desired_heading - 10:
                _steer += 5
            elif _cur_heading > _desired_heading + 2:
                _steer -= 1
            elif _cur_heading < _desired_heading - 2:
                _steer += 1 
            else:
                _steer = 0

            if _steer > 180:
                _steer -= 360
            elif _steer < -180:
                _steer += 360

            VWSetSpeed(_drive_speed, _steer)

        VWSetSpeed(0, 0)

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
            cam2image(self.img).save(current_state["img_path"])
            lidar2image(scan=list(self.scan), experiment_time=str(current_state['experiment_time']), save_path=current_state["lidar_path"])
            [current_state['loc_x'], current_state['loc_y'], current_state['loc_phi']] = VWGetPosition()
            # print(current_state)
            # save the data
            with open(self.file_path, mode='a', newline='') as file:
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
