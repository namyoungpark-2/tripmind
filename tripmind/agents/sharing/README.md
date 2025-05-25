# Sharing Agent

## 개요

Sharing Agent는 여행 일정을 다른 사용자와 공유하는 기능을 제공하는 에이전트입니다. 일정 공유 링크를 생성하고, 다양한 공유 방식을 지원합니다.

## 주요 기능

1. 일정 공유

   - 공유 링크 생성
   - 공유 기간 설정
   - 공유 권한 관리 (읽기/편집)

2. 공유 방식 지원

   - URL 공유
   - 카카오톡 공유
   - 이메일 공유
   - SMS 공유

3. 공유 관리
   - 공유 상태 추적
   - 공유 만료 관리
   - 공유 권한 검증

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── sharing/
│       ├── sharing_agent_executor.py
│       ├── sharing_agent_graph.py
│       ├── nodes/
│       │   └── sharing_node.py
│       └── utils/
│           ├── extract_info.py
│           └── validator.py
├── services/
│   └── sharing/
│       └── sharing_service.py
└── models/
    └── itinerary.py
```

## 사용 방법

### 1. 일정 공유

```python
from tripmind.agents.sharing.sharing_agent_executor import SharingRouterAgentExecutor

sharing_agent = SharingRouterAgentExecutor()
result = sharing_agent.process_prompt(
    prompt="이 일정을 친구들과 공유하고 싶어요",
    session_id="user_session_1",
    start_node="input_node"
)
```

### 2. 공유 링크 생성

```python
from tripmind.services.sharing.sharing_service import sharing_service

share_result = sharing_service.create_share_link_api(
    itinerary_id=123,
    share_type="VIEW",
    days=7,
    base_url="http://localhost:8000"
)
```

## 상태 관리

```python
class SharingRouterState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    response: Optional[str]
    context: Optional[Dict[str, Any]]
```

## 개선이 필요한 부분

1. **에러 처리**

   - 구체적인 예외 타입 정의 필요
   - 에러 복구 메커니즘 구현 필요

2. **보안**

   - 공유 링크 보안 강화 필요
   - 접근 권한 검증 강화 필요

3. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

4. **문서화**

   - API 문서화 필요
   - 코드 주석 보강 필요

5. **기능 확장**

   - 추가 공유 방식 지원 필요
   - 공유 통계 기능 추가 필요

6. **사용자 경험**
   - 공유 상태 알림 기능 필요
   - 공유 링크 관리 기능 필요
