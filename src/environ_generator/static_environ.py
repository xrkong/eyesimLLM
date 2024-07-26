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
        {self.llm_robot[0]}

        # Objects
        {self.target[0]}
        {self.static_obstacles[0]}
        {self.static_obstacles[2]}
        {self.static_obstacles[3]}
        {self.static_obstacles[4]}
                """
        with open(self.file_path, "w") as f:
            f.write(content)