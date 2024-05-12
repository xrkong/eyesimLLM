from robot import *


class EyebotLLM(EyebotBase):
    def __init__(self, speed: int = 0, angspeed: int = 0):
        super().__init__(speed, angspeed)
        self.safety_event = threading.Event()
        self.llm_request_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def control(self):
        """
        control the robot's movement based on the events
        """
        count = 0
        while True:
            if self.safety_event.is_set():
                self.logger.info("Safety event triggered!")
                # TODO: Triggering safety methods
                self.stop()
                self.safety_event.clear()
                # self.llm_request_event.set()
            # trigger a LLM request
            if self.llm_request_event.is_set():
                self.logger.info("LLM request triggered!")
                self.move(50, 0)
                # TODO: implement LLM control
                # 1. read status data from logs
                # 2. retrieve docs for planning
                # 3. organise prompt
                # 4. send prompt to LLM
                self.llm_request_event.clear()
            time.sleep(CONTROL_EVENT_CHECK_FREQUENCY)

    def user_query(self):
        """
        user query to the robot
        """
        # TODO: implement user query
        # 1. a prompt window to accept user query
        # 2. trigger request_event
        # 3. send user query to LLM
        # 4. display/record the response
        pass

    def run(self):
        """
        run the robot
        """
        self.data_collection_thread.start()
        llm_control_thread = threading.Thread(target=self.control)
        llm_control_thread.start()
        user_query_thread = threading.Thread(target=self.user_query)
        user_query_thread.start()
        self.llm_request_event.set()

        while True:
            # TODO: implement safety mechanism
            self.img = CAMGet()
            LCDImage(self.img)
            self.psd_sensor_values = [PSDGet(i) for i in range(1, 7)]
            if any(value < 200 for value in self.psd_sensor_values):
                self.safety_event.set()
            time.sleep(SAFETY_EVENT_CHECK_FREQUENCY)