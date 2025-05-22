# tripmind/application/orchestration/itinerary_agent_executor.py
from typing import Dict, Any

from .itinerary_agent_graph import itinerary_graph
from .types.itinerary_state_type import ItineraryState
from ..base_agent_excutor import BaseAgentExcutor


class ItineraryAgentExecutor(BaseAgentExcutor):
    """여행 일정 에이전트 실행기"""

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "ask_info_node",
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
            # 초기 상태 설정
            state: ItineraryState = {
                "user_input": prompt,
                "messages": [],  # 빈 메시지 배열 초기화
                "next_node": start_node,
            }
            config = {
                "configurable": {
                    "thread_id": session_id,  # 세션 ID를 thread_id로 사용
                }
            }
            # 기존 세션 불러오기 시도
            try:
                # 세션에서 메시지 및 컨텍스트 복원
                session_state = itinerary_graph.get_state(config=config)
                if session_state:
                    messages = session_state.get("messages", [])
                    # 새 사용자 메시지 추가 (extract_context에서도 추가되지만 여기서도 추가)
                    messages.append({"role": "user", "content": prompt})
                    state = {
                        **session_state,
                        "user_input": prompt,
                        "messages": messages,  # 필요하다면 여기서 메시지 업데이트
                        "next_node": start_node,
                    }

            except:
                # 세션이 없으면 새로 시작
                pass

            # 그래프 실행 - session_id 인자 제거
            print(f"state: {state}")
            result = itinerary_graph.invoke(state, config=config)

            return {
                "response": result.get("response", "응답을 생성하지 못했습니다."),
                "messages": result.get("messages", []),
                "context": result.get("context", {}),
            }
        except Exception as e:
            import traceback

            traceback.print_exc()  # 디버깅용 스택 트레이스 출력
            return {
                "response": f"[여행 일정 생성 오류] {str(e)}",
                "messages": [],
                "context": {},
            }
