import logging

from llm_call.llm_request import LLMRequest

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # req = LLAMARequest(remote_url=False, model_name="llama2-7b-chat")
    temp = LLMRequest()

    # response = req.create_chat_completion(messages)

    response = temp.local_llama( "Drive the robot straight and collision-free close to the wall in front, then turn to the right, so it is parallel to the wall (at the robot’s left-hand side) in about 15cm distance. Then let the robot drive a “lawnmower pattern”, covering the whole "
     "surface area. The robot will start from a random position and orientation. The robot should detect the end of the area and stop there.")
    logging.info(response)
