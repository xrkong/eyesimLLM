from eye import *
import time
import threading

class EyeBot:
    def __init__(self, speed, angspeed):
        self.speed = speed
        self.angspeed = angspeed
        self.safety_event = threading.Event()
        self.llm_request_event = threading.Event()
        self.psd_sensor_values = []

    def move(self, speed, angspeed):
        self.update_state(speed, angspeed)

    def stop(self):
        self.update_state(0, 0)

    def update_state(self, speed, angspeed):
        self.speed = speed
        self.angspeed = angspeed
        VWSetSpeed(self.speed, self.angspeed)

    def LLM_control(self):
        while True:
            if self.safety_event.is_set():
                # TODO: Triggering safety methods
                self.stop()
                self.safety_event.clear()
                # self.llm_request_event.set()
            # trigger a LLM request
            if self.llm_request_event.is_set():
                self.move(50, 0)
                # TODO: implement LLM control
                # 1. read status data from logs
                # 2. retrieve docs for planning
                # 3. organise prompt
                # 4. send prompt to LLM
                self.llm_request_event.clear()
            time.sleep(1)

    def user_query(self):
        # TODO: implement user query
        # 1. a prompt window to accept user query
        # 2. trigger request_event
        # 3. send user query to LLM
        # 4. display/record the response
        pass

    def run(self):
        llm_control_thread = threading.Thread(target=self.LLM_control)
        llm_control_thread.start()
        user_query_thread = threading.Thread(target=self.user_query)
        user_query_thread.start()
        self.llm_request_event.set()
        while True:
            # TODO: implement safety mechanism
            self.psd_sensor_values = [PSDGet(i) for i in range(1, 7)]
            print(self.psd_sensor_values)
            if any(value < 200 for value in self.psd_sensor_values):
                self.safety_event.set()
            time.sleep(1)