from src.environ_generator import *


class FreeEnviron(EnvironGenerator):
    def __init__(self):
        super().__init__(env_name="free-environ")
        self.static_obstacles = None
        self.dynamic_obstacles = None
