from typing import Dict, List


def user_text_prompt(position: Dict, last_execution_result: Dict, task: str = None, control_method: str = None,
                     response_schema: Dict = None, user_query: str = None, experience_states: List[Dict] = None):
    """
    Generate a user prompt for the robot control agent.
    :param task: The task description.
    :param control_method: The control method description.
    :param response_schema: The response schema.
    :param last_execution_result: The execution result.
    :param position: The position data.
    :param user_query: The user query.
    :param experience_states: The experience states.
    """

    task = """
        Control the robot to locate and approach a red can in the room, stopping 200mm in front of it, avoiding obstacles.
        """

    control_method = """
    - Use `straight` and `turn` to control the robot, you can use more than one action at a time:
      - `straight` has four parameters:
        - `distance`: 0 < distance < 400 mm (for one action)
        - `direction`: forward or backward
        - `explanation`: describes the action.
      - `turn` has four parameters:
        - `angle`: 0 < angle < 90 degrees (for one action)
        - `direction`: left or right
        - `explanation`: describes the action.
        """

    response_schema = {"situation_awareness": "describe the situation",
                       "action_list": [{"action": "straight", "distance": 50,
                                        "direction": "forward",
                                        "explanation": "move forward"},
                                       {"action": "turn", "angle": 50,
                                        "direction": "left",
                                        "explanation": "turn left"}]}

    return f"""
Task: {task}
Control Method: {control_method}
JSON Schema: {response_schema}
Position: {position}
Last Execution Result: {last_execution_result}
"""


system_prompt = """You are a robot control agent. Generate control signals based on the user prompt, 
    which includes the task, control method, response schema, camera image, lidar map, position, and the last 
    command's result. 
1. Task: Understand the goal.
2. Control Method: Use the specified method to control the robot.
3. JSON Schema: Follow the JSON format for control signals and justifications.
4. Camera Image: Use the provided camera image.
5. Lidar Map: Use the provided lidar map.
6. Position: Use the provided position data.
7. Last Execution Result: Adjust based on the last command's success or failure.
    """
