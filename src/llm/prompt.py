from typing import Dict, List


def user_text_prompt(position: Dict, last_command: str, user_query: str = None, experience_states: List[Dict] = None):
    """
    Generate a user prompt for the robot control agent.
    :param position: The position data.
    :param last_command: The execution result of last command.
    :param user_query: The user query. TBD
    :param experience_states: The experience states. TBD
    """

    task = """Control the robot to locate and approach a red can in the room, stopping 200mm in front of it, 
    avoiding obstacles."""

    control_method = """
                    Control the robot using `straight` and `turn` commands:
                    - `straight` parameters:
                      - `distance`: 0 < distance < 400 mm
                      - `direction`: forward or backward
                      - `explanation`: action description.
                    - `turn` parameters:
                      - `angle`: 0 < angle < 90 degrees
                      - `direction`: left or right
                      - `explanation`: action description.
                    """

    response_schema = {"situation_awareness": "describe the situation by analysing the position, the camera image, "
                                              "and LiDAR map, and the last command",
                       "action_list": [{"action": "straight", "distance": 50,
                                        "direction": "forward",
                                        "explanation": "move forward"},
                                       {"action": "turn", "angle": 45,
                                        "direction": "left",
                                        "explanation": "turn left"}]}

    return f"""
            Task: {task}
            Control Method: {control_method}
            JSON Schema: {response_schema}
            Position: {position}
            Last Command: {last_command}
            """


system_prompt = """You are a robot control agent. Generate control signals based on the user prompt, which includes 
the following information: 1. Task: Understand the goal. 2. Control Method: Use the specified method to control the 
robot. 3. JSON Schema: Follow the JSON format for control signals and justifications. 4. Position: The current 
position of the robot, with x, y, and phi values. 5. Last Command: The information of the last command execution. 6. 
Camera Image: A QVGA image from the front camera of the robot. 7. Lidar Map: The robot is currently positioned at the 
center of the LiDAR map (0,0). 0 degrees represents the front of the robot. The front-right quadrant spans 0° to 90°, 
and the left-front quadrant spans 270° to 360°. Identify obstacles based on the surrounding dots in the map and plan 
a path. For objects in the front (300° to 360°, 0° to 60°), consider the path with the camera image."""
