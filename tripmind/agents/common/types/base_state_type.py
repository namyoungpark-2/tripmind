from typing import TypedDict, List, Dict, Optional, Any


class BaseState(TypedDict):
    user_input: Optional[str]  # 사용자 입력
    messages: List[Dict[str, str]]  # 대화 기록
    next: Optional[str]  # 다음 노드 (이전 버전 호환용)
    next_node: Optional[str]  # 다음 노드 (input_node에서 결정됨)
    intent: Optional[str]  # 의도 이름 (디버깅용)
    query: Optional[str]  # 쿼리
    session_id: Optional[str]  # 세션 ID
    context: Optional[Dict[str, Any]]  # 컨텍스트 정보
