from src.robot import *


class EyebotManual(EyebotBase):
    def __init__(self, task_name:str="manual"):
        super().__init__(task_name)
        self.safety_event = threading.Event()
        self.manual_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def control(self):
        """
        control the robot's movement based on the events
        """
        while True:
            if self.safety_event.is_set():
                self.logger.info("Safety event triggered!")
                # TODO: Triggering safety methods
                self.stop()
                self.safety_event.clear()
                # self.llm_request_event.set()
            if self.manual_event.is_set() and not self.safety_event.is_set():
                #self.logger.info("Manual control! "+ str(self.safety_event.is_set()))
                self.manual_control()
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
        control_thread = threading.Thread(target=self.control)
        control_thread.start()
        self.manual_event.set()
        # initialize pygame
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((400, 100))
        pygame.display.set_caption("Manual Control Window")
        self.safety_check()