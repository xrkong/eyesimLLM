from src.environ_generator import *


class StaticEnviron(EnvironGenerator):
    def __init__(self):
        super().__init__(env_name="static-environ")

    def generate_random_sim(self):
        indices = random.sample(range(len(self.static_obstacles)), 4)
        content = f"""
# world
world {self.world_file}
settings VIS TRACE

# Robots
{random.choices(self.llm_robot)[0]}

# Objects
{random.choices(self.target)[0]}
{self.static_obstacles[indices[0]]}
{self.static_obstacles[indices[1]]}
{self.static_obstacles[indices[2]]}
{self.static_obstacles[indices[3]]}
        """
        with open(self.file_path, "w") as f:
            f.write(content)

    def generate_sim(self):
        content = f"""
# world
world {self.world_file}
settings VIS TRACE

# Robots
LabBot 1789 780 0
Ackermann 429 478 180
S4 232 1659 0

# Objects
Can 1663 274 90
golf 229 1091 90
Soccer 1056 600 90
Soccer 1579 1225 90

                """
        with open(self.file_path, "w") as f:
            f.write(content)