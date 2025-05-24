from typing import Dict, Any, Generator
from tripmind.agents.common.types.agent_executor_type import BaseAgentExcutor


class ItineraryService:
    def __init__(self, agent_executor: BaseAgentExcutor):
        self.agent_executor = agent_executor

    def process_message(
        self, session_id: str, message: str, start_node: str = None
    ) -> Generator[Dict[str, Any], None, None]:
        try:
            for result in self.agent_executor.process_prompt(
                prompt=message,
                session_id=session_id,
                start_node=start_node,
            ):
                if result:
                    yield result
        except Exception as e:
            yield {
                "error": str(e),
                "response": f"[대화 오류] {str(e)}",
                "messages": [],
                "context": {},
            }
