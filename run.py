import logging

from src.discrete_movement_robot.dm_eyebot_llm import DMEyebotLLM

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

    robot = DMEyebotLLM(task_name="finder_no_obs_1", model_name="gpt-4o")
    robot.run()
