from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """
    LLM 클라이언트 (Claude API 활용)
    """

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass
