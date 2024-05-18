from src.llm.llm_request import LLMRequest
from src.llm.prompt import control_prompt, system_prompt
from src.robot import *


class EyebotLLM(EyebotBase):
    def __init__(self, task_name: str="llm"):
        super().__init__(task_name=task_name)
        self.llm_request_event = threading.Event()
        self.llm_control_event = threading.Event()
        self.manual_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def execute_action_list(self, action_list: List[Dict]):
        """
        execute the list of actions
        """
        while len(action_list)>0 and self.llm_control_event.is_set():
            action = action_list.pop(0)
            self.update_state(action["speed"], action["angspeed"])
            time.sleep(action["duration"])

    def control(self):
        """
        control the robot's movement based on the events
        """
        llm = LLMRequest(system_prompt=system_prompt(), model_name='gpt-4o')

        while True:
            if self.safety_event.is_set():
                self.logger.info("Safety event triggered!")
                self.stop()
                # wait for a certain time before clearing the safety event for data collection
                time.sleep(SAFETY_EVENT_CHECK_FREQUENCY)
                self.safety_event.clear()
                self.llm_request_event.set()
            # trigger a LLM request
            if self.llm_request_event.is_set():
                self.logger.info("LLM request triggered! ")
                self.llm_request_event.clear()
                # self.move(50, 20)
                # TODO: implement LLM control
                # 1. read status data from logs
                # 2. retrieve docs for planning
                # 3. organise prompt
                prompt = control_prompt(current_state=self.to_dict(), experience_states=[], user_query="")
                # 4. send prompt to LLM
                # TODO: uncomment the following line to use openai API
                # action_list = llm.openai_query(prompt=prompt)
                # TODO: the following line is used for template testing
                action_list = [{"speed": 50, "angspeed": 0, "duration": 5},
                               {"speed": 30, "angspeed": -20, "duration": 5},
                               {"speed": 40, "angspeed": 10, "duration": 5}
                               ]

                # reset the control event to discard the previous LLM control command and accept new control command
                self.llm_control_event.clear()
                self.llm_control_event.set()
                # execute the action list
                action_execution_thread = threading.Thread(target=self.execute_action_list, args=(action_list,))
                action_execution_thread.start()

            if self.manual_event.is_set() and not self.safety_event.is_set():
                #self.logger.info("Manual control! "+ str(self.safety_event.is_set()))
                self.manual_control()
                self.llm_request_event.clear()
            # TODO: need to comment out this line in the final version
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

    def run(self, drive_mode=None):
        """
        run the robot
        """
        self.data_collection_thread.start()
        llm_control_thread = threading.Thread(target=self.control)
        llm_control_thread.start()
        user_query_thread = threading.Thread(target=self.user_query)
        user_query_thread.start()

        if drive_mode == "manual":
            self.manual_event.set()
            # initialize pygame
            pygame.init()
            pygame.font.init()
            pygame.display.set_mode((400, 100))
            pygame.display.set_caption("Manual Control Window")
        else:
            self.llm_request_event.set()
        self.safety_check()
