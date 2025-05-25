# Itinerary Agent

## 개요

Itinerary Agent는 사용자의 여행 계획을 생성하고 관리하는 에이전트입니다. 장소 검색, 일정 관리, 캘린더 연동 등의 기능을 제공하며, LLM을 활용하여 자연스러운 대화를 통해 여행 계획을 수립합니다.

## 주요 기능

1. 여행 계획 생성

   - 목적지 기반 일정 추천
   - 장소 검색 및 상세 정보 조회
   - 일정 최적화 및 조정

2. 장소 검색 및 관리

   - 카카오 API를 활용한 장소 검색
   - 장소 상세 정보 조회
   - 위치 기반 추천

3. 일정 관리

   - Google Calendar 연동
   - 일정 공유 및 협업
   - 일정 수정 및 업데이트

4. 노드 기반 처리
   - 라우터 노드: 요청 분류 및 라우팅
   - 정보 수집 노드: 사용자 정보 수집
   - 일정 생성 노드: 여행 계획 생성
   - 일정 목록 노드: 기존 일정 조회

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── itinerary/
│       ├── itinerary_agent_executor.py
│       ├── itinerary_agent_graph.py
│       ├── nodes/
│       │   ├── itinerary_node.py
│       │   ├── ask_info_node.py
│       │   ├── itinerary_list_node.py
│       │   └── router_node.py
│       ├── tools/
│       │   ├── calendar_tool.py
│       │   ├── place_search_tool.py
│       │   └── final_response_tool.py
│       └── types/
│           ├── itinerary_state_type.py
│           └── final_response_tool_type.py
├── services/
│   └── itinerary/
│       └── itinerary_service.py
└── models/
    └── itinerary.py
```

## 사용 방법

### 1. 여행 계획 생성

```python
from tripmind.agents.itinerary.itinerary_agent_executor import ItineraryAgentExecutor

itinerary_agent = ItineraryAgentExecutor()
result = itinerary_agent.process_prompt(
    prompt="서울 3박 4일 여행 계획을 만들어주세요",
    session_id="user_session_1",
    start_node="ask_info_node"
)
```

### 2. 장소 검색

```python
from tripmind.agents.itinerary.tools.place_search_tool import get_place_search_tools
from tripmind.services.place_search.kakao_place_search_service import KakaoPlaceSearchService
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient

place_search_tools = get_place_search_tools(
    KakaoPlaceSearchService(KakaoPlaceClient(os.getenv("KAKAO_REST_KEY")))
)
```

### 3. 캘린더 연동

```python
from tripmind.agents.itinerary.tools.calendar_tool import get_calendar_tools
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient

calendar_tools = get_calendar_tools(
    GoogleCalendarService(
        GoogleCalendarClient(
            os.getenv("GOOGLE_CALENDAR_ID"),
            os.getenv("GOOGLE_CREDENTIALS_PATH")
        )
    )
)
```

## 상태 관리

```python
class ItineraryState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    session_id: Optional[str]
    context: Optional[Dict[str, Any]]
    parsed_info: Optional[Dict[str, Any]]
    intermediate_steps: Optional[List[Dict[str, Any]]]
```

## 개선이 필요한 부분

1. **에러 처리**

   - 구체적인 예외 타입 정의 필요
   - 에러 복구 메커니즘 구현 필요

2. **성능 최적화**

   - 장소 검색 결과 캐싱 필요
   - API 호출 최적화 필요

3. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

4. **문서화**

   - API 문서화 필요
   - 코드 주석 보강 필요

5. **보안**

   - API 키 관리 강화 필요
   - 사용자 인증 강화 필요
