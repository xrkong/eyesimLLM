import os

import pandas as pd

from src.utils.constant import DATA_DIR

import csv


class DataCollection:
    def __init__(self):
        pass

    # def save_data(self, task_name: str, current_state: dict):
    #     file_path = f'{DATA_DIR}/{task_name}.csv'
    #     if os.path.exists(file_path):
    #         df = pd.read_csv(file_path)
    #         df = df.append(current_state, ignore_index=True)
    #     else:
    #         df = pd.DataFrame(current_state, index=[0])
    #     df.to_csv(file_path, index=False, mode='a', header=not os.path.exists(file_path))
    #
    def save_data(self, task_name: str, current_state: dict):
        file_path = f'{DATA_DIR}/{task_name}.csv'
        fieldnames = current_state.keys()

        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write headers only if the file is empty
            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(current_state)


    def load_data(self, file_path: str):
        if not os.path.exists(file_path):
            return pd.DataFrame(columns=["speed", "angspeed", "img", "psd_sensor_values", "timestamp"])
        else:
            return pd.read_csv(file_path)



