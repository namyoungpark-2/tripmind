# tripmind/application/orchestration/itinerary_agent_executor.py
from typing import Dict, Any

from .conversation_agent_graph import conversation_graph
from ..base_agent_excutor import BaseAgentExcutor


class ConversationAgentExecutor(BaseAgentExcutor):
    """일반 대화 에이전트 실행기"""

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "greeting_node",
    ) -> Dict[str, Any]:
        """
        사용자 프롬프트 처리 및 응답 생성

        Args:
            prompt: 사용자 입력
            session_id: 세션 ID

        Returns:
            응답 및 상태 정보
        """
        try:
            state = {"user_input": prompt, "messages": [], "next_node": start_node}
            config = {"configurable": {"thread_id": session_id}}

            try:
                session_state = conversation_graph.get_state(config=config)
                if session_state:
                    # 세션 데이터 복원
                    messages = session_state.get("messages", [])
                    messages.append({"role": "user", "content": prompt})
                    state = {
                        **session_state,
                        "user_input": prompt,
                        "messages": messages,
                        "next_node": start_node,
                    }
            except:
                # 세션이 없으면 새로 시작
                pass

            # 대화 전용 노드만 포함된 그래프 실행
            result = conversation_graph.invoke(state, config=config)

            return {
                "response": result.get("response", "응답을 생성하지 못했습니다."),
                "messages": result.get("messages", []),
                "context": result.get("context", {}),
            }
        except Exception as e:
            # 오류 처리
            return {"response": f"[대화 오류] {str(e)}", "messages": [], "context": {}}
