from typing import List, Dict, Optional, Any

from tripmind.agents.base_state_type import BaseState


class ItineraryState(BaseState):
    user_input: Optional[str]  # 사용자 입력
    messages: List[Dict[str, str]]  # 대화 기록
    next: Optional[str]  # 다음 노드 (이전 버전 호환용)
    next_node: Optional[str]  # 다음 노드 (input_node에서 결정됨)
    intent: Optional[str]  # 의도 이름 (디버깅용)
    destination: Optional[str]  # 여행지
    duration: Optional[str]  # 기간
    travelers: Optional[str]  # 여행자 수
    budget: Optional[str]  # 예산
    preferences: Optional[str]  # 선호사항
    special_requirements: Optional[str]  # 특별 요구사항
    query: Optional[str]  # 쿼리
    session_id: Optional[str]  # 세션 ID
    itinerary_plan: Optional[str]  # 생성된 여행 계획
    context: Optional[Dict[str, Any]]  # 컨텍스트 정보


def create_initial_state() -> ItineraryState:
    """초기 상태 생성 함수"""
    return ItineraryState(
        user_input=None,
        messages=[],
        next=None,
        next_node=None,
        intent=None,
        destination=None,
        duration=None,
        travelers=None,
        budget=None,
        preferences=None,
        special_requirements=None,
        search_results=None,
        itinerary_plan=None,
        session_id=None,
        context={},
    )
