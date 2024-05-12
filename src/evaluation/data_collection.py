import os

import pandas as pd

from src.utils.constant import DATA_DIR


class DataCollection:
    def __init__(self):
        pass

    def save_data(self, task_name:str, current_state: dict):
        file_path = f'{DATA_DIR}/{task_name}.csv'
        previous_state = self.load_data(file_path)
        df = pd.concat([previous_state, pd.DataFrame(current_state)], ignore_index=True)
        df.to_csv(file_path, index=False)

    def load_data(self, file_path: str):
        if not os.path.exists(file_path):
            return pd.DataFrame(columns=["speed", "angspeed", "img", "psd_sensor_values", "timestamp"])
        else:
            return pd.read_csv(file_path)

