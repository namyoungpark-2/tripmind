from langchain_ollama import ChatOllama
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser


class OllamaClient(BaseLLMClient):
    def __init__(self):
        self.llm = ChatOllama(model="llama3:latest")

    def get_llm(self) -> ChatOllama:
        return self.llm

    def get_output_parser(self) -> OpenAIFunctionsAgentOutputParser:
        return OpenAIFunctionsAgentOutputParser()

    def get_json_output_parser(self) -> ReActJsonSingleInputOutputParser:
        return ReActJsonSingleInputOutputParser()


ollama_client = OllamaClient()
