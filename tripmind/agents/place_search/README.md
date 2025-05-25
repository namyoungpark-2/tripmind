# Place Search Agent

## 개요

Place Search Agent는 사용자의 장소 검색 요청을 처리하는 에이전트입니다. 카카오 API를 활용하여 장소를 검색하고, 상세 정보를 제공합니다.

## 주요 기능

1. 장소 검색

   - 키워드 기반 장소 검색
   - 위치 기반 장소 검색
   - 카테고리별 장소 검색

2. 검색 결과 처리

   - 장소 기본 정보 제공 (이름, 주소, 전화번호)
   - 카테고리 정보 제공
   - 검색 결과 포맷팅

3. 노드 기반 처리
   - 정보 수집 노드: 사용자 입력 파싱
   - 검색 노드: 장소 검색 수행
   - 스트리밍 노드: 결과 전달

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── place_search/
│       ├── place_search_agent_executor.py
│       ├── place_search_agent_graph.py
│       ├── nodes/
│       │   ├── ask_info_node.py
│       │   └── place_search_node.py
│       ├── utils/
│       │   ├── formatting.py
│       │   ├── parser.py
│       │   └── query_builder.py
│       └── types/
│           ├── place_search_state_type.py
│           └── place_info_type.py
├── services/
│   └── place_search/
│       ├── base_place_search_service.py
│       └── kakao_place_search_service.py
└── clients/
    └── place_search/
        ├── base_place_search_client.py
        └── kakao_place_client.py
```

## 사용 방법

### 1. 장소 검색

```python
from tripmind.agents.place_search.place_search_agent_executor import PlaceSearchAgentExecutor

place_search_agent = PlaceSearchAgentExecutor()
result = place_search_agent.process_prompt(
    prompt="서울 강남역 근처 카페 추천해주세요",
    session_id="user_session_1",
    start_node="ask_info_node"
)
```

### 2. 검색 결과 포맷팅

```python
from tripmind.agents.place_search.utils.formatting import format_places_results

formatted_results = format_places_results(search_results)
```

## 상태 관리

```python
class PlaceSearchState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    parsed_info: Dict[str, str]
    context: Optional[Dict[str, Any]]
    streaming: Optional[Dict[str, Any]]
```

## 개선이 필요한 부분

1. **에러 처리**

   - 구체적인 예외 타입 정의 필요
   - 에러 복구 메커니즘 구현 필요

2. **성능 최적화**

   - 검색 결과 캐싱 구현 필요
   - API 호출 최적화 필요

3. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

4. **문서화**

   - API 문서화 필요
   - 코드 주석 보강 필요

5. **보안**

   - API 키 관리 강화 필요
   - 입력 데이터 검증 강화 필요

6. **확장성**
   - 추가 장소 검색 API 지원 필요
   - 검색 필터 기능 강화 필요
