from typing import Dict, List, Union

from src.discrete_movement_robot import *
from src.llm.llm_request import LLMRequest


class DMEyebotLLM(DiscreteMovementEyebot):
    def __init__(self, task_name: str, system_prompt: str = "", model_name='gpt-4o'):
        super().__init__(task_name=task_name)
        self.llm = LLMRequest(task_name=task_name, system_prompt=system_prompt, model_name=model_name)
        self.llm_action_record_file_path = f'{DATA_DIR}/{self.task_name}/llm_action_record.csv'

    def action_record_to_dict(self, action: Dict, safe: bool = False):
        key = "distance" if action["action"] == "straight" else "angle"
        return {
            "experiment_time": self.step,
            "action": action["action"],
            "distance": action[key],
            "direction": action["direction"],
            "explanation": action["explanation"],
            "safe": safe
        }

    def safety_check(self, action: Dict, range_degrees: int = 30):
        """
        check if the action is safe
        """
        # for checking the front
        offset = 179
        if action["direction"] == "backward":
            # for checking the back
            offset = 0
        if action["action"] == "straight":
            # Check distances in the range around the current direction
            for direction_to_check in range(-range_degrees, range_degrees + 1):
                distance_in_direction = self.scan[offset + direction_to_check]
                if distance_in_direction - action["distance"] < 100:
                    return False
        return True

    def execute_action_list(self, action_list: List[Dict]):
        """
        execute the list of actions
        """
        while len(action_list) > 0:
            action = action_list.pop(0)
            if not self.safety_check(action):
                self.logger.info(f"Action {action['action']} {action['distance']} {action['direction']} is not safe")
                save_item_to_csv(item=self.action_record_to_dict(action, safe=False),
                                 file_path=self.llm_action_record_file_path)
                continue
            if action["action"] == "straight":
                self.logger.info(f"Executing action {action['action']} {action['distance']} "
                                 f"{action['direction']}")
                self.straight(action["distance"], action["distance"], action['direction'])
            elif action["action"] == "turn":
                self.logger.info(f"Executing action {action['action']} {action['angle']} {action['direction']}")
                self.turn(action["angle"], action["angle"], action['direction'])
            save_item_to_csv(item=self.action_record_to_dict(action, safe=True),
                             file_path=self.llm_action_record_file_path)
            self.update_sensors()
            self.step += 1

    def run(self):
        while KEYRead() != KEY4:
            self.update_sensors()
            self.data_collection()
            current_state = self.get_current_state()
            command = self.llm.openai_query(text=current_state['text'], images=current_state['images'], experiment_time=self.step)
            self.logger.info(command["situation_awareness"])
            self.logger.info(command["action_list"])
            self.execute_action_list(command["action_list"])

