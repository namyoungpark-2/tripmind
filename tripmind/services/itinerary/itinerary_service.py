from typing import Dict

from tripmind.agents.common.types.agent_executor_type import BaseAgentExcutor


class ItineraryService:
    def __init__(self, agent_executor: BaseAgentExcutor):
        self.agent_executor = agent_executor

    def process_message(self, session_id: str, message: str, start_node: str) -> Dict:
        try:
            result = self.agent_executor.process_prompt(message, session_id, start_node)
        except Exception as e:
            return {"error": str(e)}

        return result
