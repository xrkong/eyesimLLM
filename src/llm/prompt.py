from typing import Dict, List, Tuple


def system_prompt():
    """
    TODO: need to be further designed
    I'm assuming system prompt is a high-level static prompt for a given task
    that doesn't change.
    Do we need parameters for system prompt?
    """



    return f"""
    You are a robot agent. You can use `speed`, `angspeed`, `duration` , `explanation`,
    to control the movement of the robot. 
    `speed` is the linear speed of the robot in mm/s, forward is positive and backward is negative, 
    `angspeed` is the angular speed of the robot in degrees/s, left is positive and right is negative,
    `duration` is the time duration of an action. 
    `explanation` is the explanation of the action.
    You should give a list of actions as your response for a given task. 
    You should output JSON.
    """

def control_prompt(current_state: Dict, experience_states: List[Dict], user_query: str):
    """
    TODO: need to be further designed
    Possible parameters for this prompt: current state,
    experience states (RAG), tasks to be done, user query, etc.
    """
    return f"""
    Some task description....
    Some prompt....
    {current_state}
    Some prompt....
    {experience_states}
    Some prompt....
    {user_query}
    """

def lawnmower_prompt(map_size: Tuple[int, int], current_position: Tuple[int, int]):
    user_query = f"you are a king chess (move one square in any direction) in a novel empty chessboard with x axis 0-{map_size[0]} and y axis is 0-{map_size[1]}. your start point is {current_position}. Do not generate any other answer, just print your planned lawnmower path with x0,y0|x1,y1|..."
    # TODO Check readable format
    return user_query