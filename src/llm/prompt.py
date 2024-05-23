from typing import Dict, List, Union


def system_prompt(task_description: str, control_description: str, schema: Union[List[Dict], Dict]):
    """
    TODO: need to be further designed
    I'm assuming system prompt is a high-level static prompt for a given task
    that doesn't change.
    Do we need parameters for system prompt?
    """

    return f"""
    You are a robot agent. 
    Your tasks: {task_description}
    How to control the robot: {control_description}
    You should output JSON format like this: {schema}
    """


def control_prompt(current_state: Dict, experience_states: List[Dict], user_query: str):
    """
    TODO: need to be further designed
    Possible parameters for this prompt: current state,
    experience states (RAG), tasks to be done, user query, etc.
    """
    return f"""
    current state: {current_state}
    {experience_states}
    {user_query}
    """
