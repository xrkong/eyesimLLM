import logging

from src.robot.eyebot_lawnmower import EyebotLawnmower
from src.robot.eyebot_llm import EyebotLLM
from src.robot.eyebot_manual import EyebotManual
from src.llm.prompt import system_prompt
from src.discrete_movement_robot.dm_eyebot_llm import DMEyebotLLM

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # control_description = """Use `speed`, `angspeed`, `duration`, and `explanation` to control the robot. `speed` is
    # linear in mm/s (forward>0, backward<0). `angspeed` is angular in degrees/s (turn left>0,
    # turn right<0). `duration` is the action time, and `explanation` describes the action."""
    # task_description = """The robot sends its current state, and you send back at least 2 actions to control it,
    # but you can use more if you want. The state includes speed, angular speed, a front camera image showing the front
    # scene, and a LiDAR image showing distance to all the surround wall. You need to analyse these two images
    # carefully. Control the robot to locate and approach a red can in the room, stopping 200mm in front of it."""
    #
    # schema = {"situation_awareness": "describe the situation",
    #           "action_list": [{"speed": 50, "angspeed": 0, "duration": 5, "explanation": "move forward"}]}
    # robot = EyebotLLM(task_name="llm_finder", system_prompt=system_prompt(task_description=task_description,
    #                                                                       control_description=control_description,
    #                                                                       schema=schema))
    # robot.run()

    control_description = """
- Use `straight` and `turn` to control the robot:
  - `straight` has two parameters:
    - `distance`: 0 < distance < 200 mm (for one action)
    - `speed`: mm/s 
    - `direction`: forward or backward
  - `turn` has two parameters:
    - `angle`: 0 < angle < 60 degrees (for one action)
    - `speed`: degrees/s
    - `direction`: left or right
- `duration`: specifies the action time
- `explanation`: describes the action.
    """
    task_description = """
The robot sends its current state, and you send back at least one action. The state includes:
- `position` (x, y, phi)
- A front camera image showing the front scene
- A LiDAR image showing the distance to all surrounding objects

Your task is to control the robot to locate and approach a red can in the room, stopping 200mm in front of it. 
    
    """

    schema = {"situation_awareness": "describe the situation",
              "action_list": [{"action": "straight", "distance": 50, "speed": 10,
                               "direction": "forward",
                               "explanation": "move forward"},
                              {"action": "turn", "angle": 50, "speed": 10,
                               "direction": "left",
                               "explanation": "turn left"}]}
    robot = DMEyebotLLM(task_name="discrete_llm_finder", system_prompt=system_prompt(task_description=task_description,
                                                                                     control_description=control_description,
                                                                                     schema=schema))
    robot.run()
