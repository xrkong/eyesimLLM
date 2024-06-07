from src.robot import *
from src.scripts.lawnmower import S4_Robot


class EyebotLawnmower:
    def __init__(self):
        super().__init__(task_name="lawnmower")

    def run(self):
        S4_Robot().robot_trajectory()
