import random


class EnvironGenerator:
    def __init__(self, env_name: str):
        self.env_name = env_name
        self.file_path = f"/opt/eyesim/eyesimX/{self.env_name}.sim"
        self.world_file = "/opt/eyesim/eyesimX/test.wld"
        self.llm_robot = ["S4 999 500 89", "S4 999 500 89", "S4 999 500 89", "S4 999 500 89"]
        self.target = ["Can 1716 1784 90", "Can 1716 1784 90", "Can 1716 1784 90", "Can 1716 1784 90"]
        self.dynamic_obstacles = []
        self.static_obstacles = []

    def generate_random_sim(self):
        content = f"""
# world
{self.world_file}

# Robots
{random.choices(self.llm_robot)}
{random.sample(self.dynamic_obstacles, 2)}

# Objects
{random.choices(self.target)}
{random.sample(self.static_obstacles, 4)}
        """
        with open(self.file_path, "w") as f:
            f.write(content)
