import logging
from llm_request import LLMRequest

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    req = LLMRequest(model_name="Mixtral-8x7b")
    req.get_completion(prompt="What is the capital of France?")
