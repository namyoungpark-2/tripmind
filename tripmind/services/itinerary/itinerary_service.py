from typing import Dict

from tripmind.agents.common.executor.base_agent_excutor import BaseAgentExcutor


class ItineraryService:
    """
    여행 일정 서비스
    """

    def __init__(self, agent_executor: BaseAgentExcutor):
        self.agent_executor = agent_executor

    def process_message(self, session_id: str, message: str, start_node: str) -> Dict:
        """
        사용자 메시지 처리

        Args:
            session_id: 세션 ID
            message: 사용자 메시지

        Returns:
            처리 결과
        """

        try:
            result = self.agent_executor.process_prompt(message, session_id, start_node)
        except Exception as e:
            return {"error": str(e)}

        return result
