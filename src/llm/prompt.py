from typing import Dict, List


def user_text_prompt(
    position: Dict,
    last_command: str,
    user_query: str = None,
    experience_states: List[Dict] = None,
):
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
                    - `straight`:
                      - `distance`: 0 < distance < 400 mm
                      - `direction`: forward or backward
                    - `turn`:
                      - `angle`: 0 < angle < 90 degrees
                      - `direction`: left or right
                    """

    response_schema = {
        "perception": {
            "situation": "Analyse the position, the camera image, "
            "and LiDAR map, and the last command",
            "target": "Estimate the target position based on the perception",
        },
        "planning": "A plan based on the perception, the plan need to include control "
        "signals with justifications",
        "control": [{"action": "straight", "distance": 50, "direction": "forward"}],
    }

    # response_schema = {
    #     "$schema": "http://json-schema.org/draft-07/schema#",
    #     "title": "Response Schema",
    #     "description": "Schema for the robot control agent's response",
    #     "type": "object",
    #     "properties": {
    #         "perception": {
    #             "type": "object",
    #             "description": "Information about the robot's perception",
    #             "properties": {
    #                 "situation": {
    #                     "type": "string",
    #                     "description": "Analysis of the position, camera image, LiDAR map, and the last command",
    #                     "example": "The robot is at position (x, y), the camera image shows an obstacle ahead, "
    #                     "the LiDAR map indicates a clear path to the left, the last command was to move "
    #                     "forward.",
    #                 },
    #                 "target": {
    #                     "type": "string",
    #                     "description": "Estimated target position based on the perception",
    #                     "example": "Target position is at (x+10, y+5).",
    #                 },
    #             },
    #             "required": ["situation", "target"],
    #         },
    #         "planning": {
    #             "type": "string",
    #             "description": "Plan based on the perception including control signals with justifications",
    #             "example": "Move forward 50 units to avoid the obstacle, then turn left and proceed to the target "
    #             "position.",
    #         },
    #         "control": {
    #             "type": "array",
    #             "description": "List of control actions to be executed",
    #             "items": {
    #                 "type": "object",
    #                 "oneOf": [
    #                     {
    #                         "type": "object",
    #                         "properties": {
    #                             "action": {
    #                                 "type": "string",
    #                                 "enum": ["straight"],
    #                                 "description": "The type of action to be performed",
    #                                 "example": "straight",
    #                             },
    #                             "distance": {
    #                                 "type": "number",
    #                                 "minimum": 1,
    #                                 "maximum": 300,
    #                                 "description": "The distance for the straight action in millimeters",
    #                                 "example": 50,
    #                             },
    #                             "direction": {
    #                                 "type": "string",
    #                                 "enum": ["forward", "backward"],
    #                                 "description": "The direction for the straight action",
    #                                 "example": "forward",
    #                             },
    #                         },
    #                         "required": ["action", "distance", "direction"],
    #                     },
    #                     {
    #                         "type": "object",
    #                         "properties": {
    #                             "action": {
    #                                 "type": "string",
    #                                 "enum": ["turn"],
    #                                 "description": "The type of action to be performed",
    #                                 "example": "turn",
    #                             },
    #                             "angle": {
    #                                 "type": "number",
    #                                 "minimum": 1,
    #                                 "maximum": 60,
    #                                 "description": "The angle for the turn action in degrees",
    #                                 "example": 45,
    #                             },
    #                             "direction": {
    #                                 "type": "string",
    #                                 "enum": ["left", "right"],
    #                                 "description": "The direction for the turn action",
    #                                 "example": "left",
    #                             },
    #                         },
    #                         "required": ["action", "angle", "direction"],
    #                     },
    #                 ],
    #             },
    #         },
    #     },
    #     "required": ["perception", "planning", "control"],
    # }

    return f"""
            Task: {task}
            Control Method: {control_method}
            JSON Schema: {response_schema}
            Position: {position}
            Last Command: {last_command}
            """


system_prompt = """You are a robot control agent. Generate control signals based on the user prompt, which includes 
the following information: 1. Task: Understand the goal. 2. JSON Schema: Follow the JSON format for control signals 
and justifications. 3. Position: The current position of the robot, with x, y, and phi values. 4. Last Command: The 
information of the last command execution. 5. Camera Image: A QVGA image from the front camera of the robot. 6. Lidar 
Map: The robot is currently positioned at the center of the LiDAR map (0,0). 0 degrees represents the front of the 
robot. The front-right quadrant spans 0° to 90°, and the left-front quadrant spans 270° to 360°. Identify obstacles 
based on the surrounding dots in the map and plan a path. For objects in the front (300° to 360°, 0° to 60°), 
consider the path with the camera image."""
