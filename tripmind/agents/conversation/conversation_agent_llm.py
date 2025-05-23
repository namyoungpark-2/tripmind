import os
from langchain_anthropic import ChatAnthropic

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")


class ConversationAgentLLM:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
        self.llm = ChatAnthropic(model=MODEL, anthropic_api_key=api_key)

    def get_llm(self):
        return self.llm


conversation_agent_llm = ConversationAgentLLM()
