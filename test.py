import logging

import argparse
from src.discrete_robot.discrete_llm_robot import DMLLMEyebot
from src.environ_generator.static_environ import StaticEnviron

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the robot with different prompts.')
    parser.add_argument('model', type=str, default="gpt-4o", choices=['gpt-4o', 'gpt-4o-mini'])
    parser.add_argument("attack", type=str, default="none", choices=['none', 'naive', 'image', 'noise'])
    parser.add_argument("defence", type=str, default="none", choices=['none', 'agent', 'self'])
    parser.add_argument("attack_rate", type=float, default=0.5, choices=[0.1, 0.3, 0.5, 0.7, 1])

    args = parser.parse_args()
    attack = args.attack
    model = args.model
    defence = args.defence
    attack_rate = args.attack_rate

    robot = DMLLMEyebot(task_name=f"{model}_{attack}_{defence}_rate{attack_rate}",
                        attack=attack,
                        model_name=model,
                        attack_rate=attack_rate,
                        defence=defence)
    robot.run(security=True)
