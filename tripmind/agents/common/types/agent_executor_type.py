from typing import TypedDict


class AgentExecutorResult(TypedDict):
    response: str
    messages: list
    context: dict
    intent: str
    next_node: str


class BaseAgentExcutor:
    def __init__(self):
        pass

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "input_node",
    ) -> AgentExecutorResult:
        pass
