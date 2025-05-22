from typing import Dict

from tripmind.agents.excutors.base_agent_excutor import BaseAgentExcutor


class LangGraphService:
    """
    LangGraph 기반 멀티 에이전트 서비스
    """

    def __init__(self, agent_executor: BaseAgentExcutor):
        self.agent_executor = agent_executor

    def process_message(self, session_id: str, message: str) -> Dict:
        """
        사용자 메시지 처리

        Args:
            session_id: 세션 ID
            message: 사용자 메시지

        Returns:
            처리 결과
        """

        try:
            result = self.agent_executor.process_prompt(message, session_id)
        except Exception as e:
            return {"error": str(e)}

        return result
