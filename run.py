import logging
from src.robot.eyebot_llm import EyebotLLM

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    robot = EyebotLLM(speed=0, angspeed=0)
    robot.run()
