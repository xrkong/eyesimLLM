from src.discrete_movement_robot import *
from src.llm.llm_request import LLMRequest


class DMEyebotLLM(DiscreteMovementEyebot):
    def __init__(self, task_name: str, system_prompt: str = ""):
        super().__init__(task_name=task_name)
        self.system_prompt = system_prompt

    def execute_action_list(self, action_list: List[Dict]):
        """
        execute the list of actions
        """
        while len(action_list) > 0:
            action = action_list.pop(0)
            if action["action"] == "straight":
                self.logger.info(f"Executing action {action['action']} {action['distance']} "
                                 f"{action['speed']} {action['direction']}")
                self.straight(action["distance"], action["speed"], action['direction'])
            elif action["action"] == "turn":
                self.logger.info(f"Executing action {action['action']} "
                                 f"{action['angle']} {action['speed']} {action['direction']}")
                self.turn(action["angle"], action["speed"], action['direction'])
            self.update_sensors()
            self.step += 1

    def run(self):
        llm = LLMRequest(task_name=self.task_name, system_prompt=self.system_prompt, model_name='gpt-4o')
        while KEYRead() != KEY4:
            self.update_sensors()
            self.data_collection()
            current_state = self.get_current_state()
            command = llm.openai_query(text=current_state['text'], images=current_state['images'])
            self.logger.info(command["situation_awareness"])
            self.logger.info(command["action_list"])
            self.execute_action_list(command["action_list"])

