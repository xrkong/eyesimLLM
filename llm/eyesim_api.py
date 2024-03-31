from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.chat_models import Llama2Chat
from os.path import expanduser

from langchain_community.llms import LlamaCpp


class EyesimAPI:
    def __init__(self):
        self.llm_chain = LLMChain(model=Llama2Chat)
        self.memory = ConversationBufferMemory()

    def get_response(self, prompt: str):
        response = self.llm_chain.get_response(prompt)
        self.memory.add_conversation(prompt, response)
        return response
