from typing import Dict, List, Union
import json
from src.discrete_movement_robot import *
from src.discrete_movement_robot.action import Action
from src.llm.llm_request import LLMRequest
from src.llm.prompt import system_prompt_text, user_prompt_text
from src.llm.prompt_tools import tools, system_prompt_tools, user_prompt_tools
import numpy as np


class DMEyebotLLM(DiscreteMovementEyebot):
    def __init__(self, task_name: str, model_name="gpt-4o"):
        super().__init__(task_name=task_name)
        self.model_name = model_name
        self.llm_action_record_file_path = (
            f"{DATA_DIR}/{self.task_name}/llm_action_record.csv"
        )
        self.llm = LLMRequest(task_name=self.task_name, model_name=self.model_name)

    @staticmethod
    def red_detector(img):
        """
        Returns the column with the most red pixels in the image.
        """
        hsi = IPCol2HSI(img)

        hue = np.array(hsi[0]).reshape(QVGA_Y, QVGA_X)
        red = np.where(hue > ctypes.c_int(20))

        if len(red[0]) == 0:
            return [False, 0, 0]

        for i in range(len(red[0])):
            LCDPixel(red[1][i], red[0][i], RED)

        red_count = np.bincount(red[1])  # count the number of red pixels in each column
        # print histogram
        for i in range(len(red_count)):
            LCDLine(i, QVGA_Y, i, QVGA_Y - red_count[i], RED)

        # find the column with the most red pixels
        max_col = np.argmax(red_count)
        max = red_count[max_col]
        return [True, max_col, max]

    def execute_action_list(self):
        """
        execute the list of actions
        """
        for i, act in enumerate(self.last_command):
            # Updating pos_before of the action object
            act.pos_before = {"x": self.x, "y": self.y, "phi": self.phi}

            # Initial pos_after is set to the same as pos_before
            act.pos_after = {"x": self.x, "y": self.y, "phi": self.phi}

            # Check if the action is safe
            if not act.is_safe(self.scan, range_degrees=10):
                self.logger.info(
                    f"Action {act.action} distance={act.distance} direction={act.direction} is not safe"
                )
                save_item_to_csv(
                    act.to_dict(experiment_time=self.step),
                    file_path=self.llm_action_record_file_path,
                )
                break

            # Mark action as executed
            act.executed = True
            self.logger.info(
                f"Executing action {act.action} distance={act.distance} angle={act.angle} direction={act.direction}"
            )

            # Execute the action based on its type
            if act.action == "straight":
                self.straight(act.distance, act.distance, act.direction)
            elif act.action == "turn":
                self.turn(act.angle, act.angle, act.direction)

            # Update pos_after to reflect the new position after execution
            act.pos_after = {"x": self.x, "y": self.y, "phi": self.phi}

            # Save the action's details to a CSV file
            save_item_to_csv(
                act.to_dict(experiment_time=self.step),
                file_path=self.llm_action_record_file_path,
            )

            # Update sensors and increment step
            self.update_sensors()
            self.step += 1

    def run(self):
        max_value = 0
        while KEYRead() != KEY4 and max_value < 180:
            task = input("Enter the task: ")
            #BUG the task should input once, not every round. 

            # defense user attack. Check the input prompt is legal or not. If not DO nothing.
            if not self.llm.is_legal_input(task):
                continue #TODO add the defense mechanism to the LLM

            self.update_sensors()
            self.data_collection()
            [res, max_col, max_value] = self.red_detector(self.img) # TODO red detector will be called by the LLM
            current_state = self.get_current_state()

            # TODO use AutoGen to filter malicious commands
            content = self.llm.openai_query(
                system_prompt=system_prompt_text,
                text=user_prompt_text(
                    task=task,
                    position=current_state["position"],
                    last_command=current_state["last_command"],
                ),
                images=current_state["images"]
            )
            
            # check control command safety


            # BUG if the content is not legal, the process will throw an exception here.
            response_record = self.llm.llm_response_record(
                self.step,
                content["perception"],
                content["planning"],
                content["control"],
            )
            save_item_to_csv(item=response_record, file_path=self.file_path)

            self.logger.info(content["perception"])
            self.logger.info(content["planning"])
            self.logger.info(content["control"])

            self.last_command = [
                Action(
                    action=a.get("action"),
                    direction=a.get("direction"),
                    distance=a.get("distance", 0),
                    angle=a.get("angle", 0),
                )
                for a in content["control"]
            ]

            self.execute_action_list()

            # content, tool_calls = self.llm.openai_query_function_call(
            #     system_prompt=system_prompt_tools,
            #     text=user_prompt_tools(
            #         position=current_state["position"],
            #         last_command=current_state["last_command"],
            #     ),
            #     images=current_state["images"],
            #     tools=tools,
            # )
            # control = [
            #     {
            #         'action': a.function.name,
            #         'direction': json.loads(a.function.arguments).get("direction"),
            #         'distance': json.loads(a.function.arguments).get("distance", 0),
            #         'angle': json.loads(a.function.arguments).get("angle", 0),
            #     }
            #     for a in tool_calls
            # ]
            #
            # response_record = self.llm.llm_response_record(
            #     self.step, content["perception"], content["planning"], control
            # )
            # save_item_to_csv(item=response_record, file_path=self.file_path)
            #
            # self.logger.info(content["perception"])
            # self.logger.info(content["planning"])
            # self.logger.info(control)
            #
            # self.last_command = [
            #     Action(
            #         action=a.get("action"),
            #         direction=a.get("direction"),
            #         distance=a.get("distance", 0),
            #         angle=a.get("angle", 0),
            #     )
            #     for a in control
            # ]
            #
            # self.execute_action_list()
