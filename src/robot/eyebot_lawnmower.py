from src.robot import *
from src.scripts.lawnmower import S4_Robot


class EyebotLawnmower:
    def __init__(self,task_name:str, speed: int = 0, angspeed: int = 0):
        super().__init__(task_name=task_name, speed=speed, angspeed=angspeed)

    def run(self):
        S4_Robot().robot_trajectory()

