from abc import abstractmethod
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.output_parsers import BaseOutputParser


class BaseLLMClient:
    @abstractmethod
    def get_llm(self) -> BaseLanguageModel:
        pass

    @abstractmethod
    def get_output_parser(self) -> BaseOutputParser:
        pass

    @abstractmethod
    def get_json_output_parser(self) -> BaseOutputParser:
        pass
