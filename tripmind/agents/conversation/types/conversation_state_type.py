from typing import List, Dict, Optional, Any

from tripmind.agents.common.types.base_state_type import BaseState


class ConversationState(BaseState):
    user_input: Optional[str]  # 사용자 입력
    messages: List[Dict[str, str]]  # 대화 기록
    next: Optional[str]  # 다음 노드 (이전 버전 호환용)
    next_node: Optional[str]  # 다음 노드 (input_node에서 결정됨)
    intent: Optional[str]  # 의도 이름 (디버깅용)
    query: Optional[str]  # 쿼리
    session_id: Optional[str]  # 세션 ID
    context: Optional[Dict[str, Any]]  # 컨텍스트 정보


def create_initial_state() -> ConversationState:
    """초기 상태 생성 함수"""
    return ConversationState(
        user_input=None,
        messages=[],
        next=None,
        next_node=None,
        intent=None,
        query=None,
        session_id=None,
        context={},
    )
