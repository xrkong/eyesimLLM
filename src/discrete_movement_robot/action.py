import logging
from typing import Dict


class Action:
    def __init__(
        self, action: str, direction: str = "", distance: int = 0, angle: int = 0
    ):
        self.logger = logging.getLogger(__name__)
        self.action = action
        self.direction = direction
        self.distance = distance
        self.angle = angle
        self.safe = True
        self.executed = False
        self.pos_before = {}
        self.pos_after = {}

    def to_str(self) -> str:
        return (
            f"Action: {self.action}, "
            f"Direction: {self.direction}, "
            f"Distance: {self.distance}, "
            f"Angle: {self.angle}),"
            f"Safety Check Result: {self.safe}, "
            f"Executed Or Not: {self.executed}"
            f"Position Before: {self.pos_before}"
            f"Position After: {self.pos_after}"
        )

    def to_dict(self, experiment_time: int) -> Dict:
        return {
            "experiment_time": experiment_time,
            "action": self.action,
            "direction": self.direction,
            "distance": self.distance,
            "angle": self.angle,
            "safe": self.safe,
            "executed": self.executed,
            "pos_before": self.pos_before,
            "pos_after": self.pos_after,
        }

    def from_dict(self, action_dict: Dict):
        self.action = action_dict["action"]
        self.direction = action_dict["direction"]
        self.distance = action_dict["distance"]
        self.angle = action_dict["angle"]

    def is_safe(self, scan: Dict, range_degrees: int = 30) -> bool:
        """
        check if the action is safe
        """
        # for checking the front
        offset = 179
        if self.direction == "backward":
            # for checking the back
            offset = 0
        for direction_to_check in range(-range_degrees, range_degrees + 1):
            distance_in_direction = scan[offset + direction_to_check]
            if distance_in_direction - abs(self.distance) < 100:
                self.safe = False
                return False
        return True

