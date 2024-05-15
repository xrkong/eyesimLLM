import logging

from src.robot.eyebot_lawnmower import EyebotLawnmower
from src.robot.eyebot_llm import EyebotLLM

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    robot = EyebotLLM(task_name="llm_test", speed=0, angspeed=0)
    # robot  = EyebotLawnmower(task_name="lawnmower_test", speed=0, angspeed=0)
    robot.run(drive_mode="manual")
