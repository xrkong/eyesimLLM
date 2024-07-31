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

        wld_content = f"""
floor 2000 2000
0 2000 0 0
2000 2000 2000 0
2000 0 0 0
-7 2004 2023 2019
1011 1984 1019 1173
0 320 1181 324
        
        """

        with open(self.world_file, "w") as f:
            f.write(wld_content)

        content = f"""
# world
world {self.world_file}
settings TRACE

# Robots
LabBot 1789 780 0 swarm.py
S4 232 1659 0 s4.py

# Objects
Can 1663 274 90
Soccer 229 1291 90
Soccer 1579 1425 90

                """
        with open(self.file_path, "w") as f:
            f.write(content)