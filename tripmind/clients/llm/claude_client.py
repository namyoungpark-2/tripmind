import os
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain.llms.base import BaseLLM
from pydantic import BaseModel
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from langchain.output_parsers import PydanticOutputParser


class ClaudeClient(BaseLLMClient):
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.llm: Optional[BaseLLM] = ChatAnthropic(
            model=model, anthropic_api_key=api_key
        )

    def get_llm(self) -> BaseLLM:
        return self.llm

    def get_output_parser(self, pydantic_object: BaseModel) -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=pydantic_object)


claude_client = ClaudeClient()
