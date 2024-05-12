from src.robot import *
from src.scripts.lawnmower import S4_Robot


class EyebotLawnmower(EyebotBase):
    def __init__(self, speed: int = 0, angspeed: int = 0):
        super().__init__(speed, angspeed)

    def run(self):
        S4_Robot().robot_trajectory()

