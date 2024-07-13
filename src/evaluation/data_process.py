import pandas as pd
import os
from src.utils.constant import DATA_DIR

if __name__ == '__main__':
    task_name = 'finder_no_obs_security'

    steps = []
    tokens = []
    distances = []

    for i in range(0, 6):
        if os.path.isdir(DATA_DIR / f"{task_name}_{str(i)}") is False:
            continue
        llm_action_record = pd.read_csv(DATA_DIR / f"{task_name}_{str(i)}" / 'llm_action_record.csv')
        llm_reasoning_record = pd.read_csv(DATA_DIR / f"{task_name}_{str(i)}" / 'llm_reasoning_record.csv')

        total_steps = llm_action_record['step'].max()
        total_tokens = llm_reasoning_record['total_tokens'].sum()
        distance = llm_action_record[llm_action_record['executed'] == True]['distance'].sum()

        steps.append(total_steps)
        tokens.append(total_tokens)
        distances.append(distance)

    print("average steps: " + str(sum(steps) / len(steps)))

    print("average tokens: " + str(sum(tokens) / len(tokens)))

    print("average distance: " + str(sum(distances) / len(distances)))

