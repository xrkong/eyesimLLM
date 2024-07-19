from typing import Dict, List, Union
import json
from src.discrete_robot import *
from src.discrete_robot.action import Action
from src.llm.llm_request import LLMRequest
from src.llm.prompt import system_prompt_text, user_prompt_text
from src.llm.prompt_tools import tools, system_prompt_tools, user_prompt_tools
import numpy as np
import os
import threading
import shutil


class DMLLMEyebot(DiscreteRobot):
    def __init__(self, task_name: str, model_name="gpt-4o", human_instruction="", attack_frequency=0.5):
        super().__init__(task_name=self.number_task_name_folder(task_name))
        self.model_name = model_name
        self.llm_action_record_file_path = (
            f"{DATA_DIR}/{self.task_name}/llm_action_record.csv"
        )
        self.llm = LLMRequest(task_name=self.task_name, model_name=self.model_name)
        self.human_instruction = human_instruction
        self.safety_event = threading.Event()

    def number_task_name_folder(self, task_name):
        """
        Set the number of folders in the data directory
        """
        # check if any folder prefix with the task name
        max_num = 0
        for folder in os.listdir(DATA_DIR):
            if folder.startswith(task_name):
                # get the number after the task name
                number = folder.split("_")[1]
                if number.isnumeric() and int(number) > max_num:
                    max_num = int(number)
        return f"{task_name}_{str(max_num+1)}"

    def safety_check(self):
        """
        Check if the robot is in a safe state
        """
        while True:
            scanned_result = LIDARGet()
            for dist in scanned_result:
                if dist < 20:
                    self.safety_event.set()
                    self.logger.info("Safety event triggered!")
                    return
            time.sleep(1)

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

    def validate_and_execute_action_list(self):
        flag = True
        self.step += 1
        for i, act in enumerate(self.last_command):
            if not act.is_safe(self.scan, range_degrees=10):
                # Updating pos_before of the action object
                act.pos_before = {"x": self.x, "y": self.y, "phi": self.phi}
                # Initial pos_after is set to the same as pos_before
                act.pos_after = {"x": self.x, "y": self.y, "phi": self.phi}
                self.logger.info(f"Action {act.action} distance={act.distance} direction={act.direction} is not safe")
                save_item_to_csv(act.to_dict(step=self.step), file_path=self.llm_action_record_file_path)
                flag = False
            if flag:
                self.execute_action(act)

        return flag

    def execute_action(self, act):
        """
        execute the list of actions
        """
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

        # Update sensors and increment step
        self.update_sensors()

        [res, max_col, max_value] = self.red_detector(self.img)

        # Save the action's details to a CSV file
        save_item_to_csv(
            act.to_dict(step=self.step, target_lost=(max_value == 0)),
            file_path=self.llm_action_record_file_path,
        )

    def run(self, security: bool = False, camera=True, lidar=True):
        osid= OSMachineID()
        print("my id %d\n" % osid)  # to console
        max_value = 0
        # human_instruction = input("Enter the instruction: ")
        max_step = 20
        # safety_check_thread = threading.Thread(target=self.safety_check)
        # safety_check_thread.start()
        self.update_sensors()
        i = 0
        while KEYRead() != KEY4 and max_value < 100 and self.step < max_step and not self.safety_event.is_set():
            i += 1
            self.data_collection()
            current_state = self.get_current_state(camera, lidar)

            is_executable = False
            failure_threshold = 1
            if security:
                failure_threshold = 3
            while not is_executable and failure_threshold > 0:
                content, usage = self.llm.openai_query(
                    system_prompt=system_prompt_text(security=security),
                    text=user_prompt_text(
                        i = i,
                        human_instruction=self.human_instruction,
                        last_command=current_state["last_command"],
                        security=security,
                    ),
                    images=current_state["images"]
                )
                response_record = self.llm.llm_response_record(
                    self.step + 1,
                    content["perception"],
                    content["planning"],
                    content["control"],
                    usage.completion_tokens,
                    usage.prompt_tokens,
                    usage.total_tokens,
                )
                save_item_to_csv(item=response_record, file_path=self.llm.file_path)

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

                is_executable = self.validate_and_execute_action_list()
                failure_threshold -= 1
                self.logger.info("is_executable: " + str(is_executable))
                self.logger.info("failure threshold: " + str(failure_threshold))
            if not is_executable:
                break
            self.update_sensors()
            [res, max_col, max_value] = self.red_detector(self.img)
            self.logger.info("max value:" + str(max_value))

        if max_value >= 100:
            self.logger.info("Mission accomplished")
        elif self.step >= max_step:
            self.logger.info("Mission timed out")
            move_directory_contents(f"{DATA_DIR}/{self.task_name}", f"{DATA_DIR}/{self.task_name}_survived")
        else:
            self.logger.info("Mission failed")
            move_directory_contents(f"{DATA_DIR}/{self.task_name}", f"{DATA_DIR}/{self.task_name}_failed")


def move_directory_contents(src, dst):
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else:
            shutil.move(s, d)
    os.rmdir(src)