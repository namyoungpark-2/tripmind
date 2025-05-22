import re
from typing import Dict, Any

from tripmind.agents.types.travel_agent_state_type import TravelAgentState

def input_node(state: TravelAgentState) -> Dict[str, Any]:    
    """
    사용자 입력 분석 및 의도 파악 노드
    
    - 사용자 메시지를 받아 state에 추가
    - 여행 정보(목적지, 기간 등) 추출
    - 의도 분석 및 다음 노드 결정
    """
    user_input = state.get("user_input", "")
    context = state.get("context", {})

    # 메시지가 없으면 초기화
    if "messages" not in state:
        state["messages"] = []
    
    # 사용자 메시지 추가
    state["messages"].append({"role": "user", "content": user_input})
    
    # 1. 여행 정보 추출
    travel_info = extract_travel_info(user_input)
    
    # 추출된 정보를 context에 추가
    for key, value in travel_info.items():
        if value:
            context[key] = value
    
    # 2. 의도 분석 및 다음 노드 결정
    next_node = determine_next_node(user_input, state["messages"])

    # 저장할 정보 준비
    updated_state = {
        **state, 
        "context": context,
        "response": user_input,
        "next_node": next_node,  # 다음 노드 저장
        "intent": get_intent_name(next_node)  # 의도 이름 저장 (디버깅용)
    }
    
    return updated_state

def extract_travel_info(text: str) -> Dict[str, str]:
    """사용자 메시지에서 여행 정보 추출"""
    info = {}
    
    # 목적지 추출 (도시명 + 국가명 패턴)
    destination_pattern = r'([가-힣a-zA-Z]+)[,\s]?\s?([가-힣a-zA-Z]+)'
    destination_match = re.search(destination_pattern, text)
    if destination_match:
        info["destination"] = destination_match.group(0)
    
    # 여행 기간 추출
    duration_patterns = [
        r'(\d+)[박]?\s?(\d+)?[일]?',  # "3박 4일", "5일"
        r'(\d+)[\s]?일[\s]?동안',  # "5일 동안"
        r'(\d+)[\s]?박[\s]?(\d+)[\s]?일'  # "3박 4일"
    ]
    
    for pattern in duration_patterns:
        duration_match = re.search(pattern, text)
        if duration_match:
            info["duration"] = duration_match.group(0)
            break
    
    # 여행자 수 추출
    travelers_match = re.search(r'(\d+)[\s]?명', text)
    if travelers_match:
        info["travelers"] = travelers_match.group(0)
    
    # 예산 추출
    budget_match = re.search(r'(\d+)[\s]?만원|(\d+)[\s]?원', text)
    if budget_match:
        info["budget"] = budget_match.group(0)
    
    return info

def determine_next_node(user_input: str, messages: list) -> str:
    """
    사용자 입력과 대화 기록을 분석하여 다음 노드 결정
    
    Args:
        user_input: 사용자 입력 문자열
        messages: 대화 기록
        
    Returns:
        다음 노드 이름 (예: "greeting", "itinerary", "calendar" 등)
    """
    # 메시지가 없으면 인사 노드로
    if not messages:
        return "greeting"
    
    # 사용자 입력 소문자 변환
    text = user_input.lower()
    
    # 1. 종료 요청 확인
    if any(kw in text for kw in ["종료", "끝", "그만"]):
        return "end"
    
    # 2. 캘린더 관련 확인
    calendar_patterns = [
        r'일정[을를]?\s*(?:추가|등록|확인|보여|조회)',
        r'캘린더',
        r'스케줄',
        r'약속',
        r'미팅',
        r'(?:오늘|내일|모레|이번주|이번\s*달)[의]?\s*일정'
    ]
    
    for pattern in calendar_patterns:
        if re.search(pattern, text):
            return "calendar"
    
    # 3. 장소 검색 관련 확인
    place_search_patterns = [
        r'(.+)(?:어디|위치|찾아|검색)',
        r'(.+)(?:이|가) 어디',
        r'(.+) 알려',
        r'근처.+찾아',
        r'(.+) 장소',
    ]
    
    place_keywords = ["위치", "찾아줘", "검색해줘", "어디", "알려줘", "근처", "주변"]
    
    if any(kw in text for kw in place_keywords):
        return "place_search"
        
    for pattern in place_search_patterns:
        if re.search(pattern, text):
            return "place_search"
    
    # 4. 일정 공유 관련 확인
    share_patterns = [
        r'일정[\s]*(?:공유|공개)',
        r'(?:공유|공개)[\s]*(?:링크|URL)',
        r'(?:친구|가족|같이|동료)[\s]*(?:에게|한테|와|과|랑)[\s]*(?:공유|보여|전달)',
        r'url[\s]*(?:생성|만들어|보내)',
        r'공유[\s]*(?:하고 싶어|하고싶어|좀)',
    ]
    
    for pattern in share_patterns:
        if re.search(pattern, text):
            return "sharing"
    
    # 5. 일정 생성 관련 확인
    itinerary_keywords = ["일정", "계획", "스케줄", "짜줘", "만들어", "여행"]
    
    if any(kw in text for kw in itinerary_keywords):
        return "itinerary"
    
    # 6. 첫 메시지인 경우 인사 노드로
    if len(messages) <= 1:  # 방금 추가한 메시지만 있는 경우
        return "greeting"
    
    # 기본값: 일반 대화
    return "conversation"

def get_intent_name(node_name: str) -> str:
    """노드 이름에 따른 의도 이름 반환 (디버깅용)"""
    intent_map = {
        "greeting": "인사",
        "itinerary": "일정생성",
        "ask_info": "정보요청",
        "place_search": "장소검색",
        "calendar": "캘린더관리",
        "conversation": "일반대화",
        "sharing": "일정공유",
        "end": "대화종료"
    }
    
    return intent_map.get(node_name, "알수없음")