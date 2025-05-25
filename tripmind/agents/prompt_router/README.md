# Prompt Router Agent

## 개요

Prompt Router Agent는 사용자의 입력을 분석하여 적절한 에이전트로 라우팅하는 역할을 수행합니다. 의도 분석과 컨텍스트 관리를 통해 효율적인 대화 처리를 지원합니다.

## 주요 기능

1. 의도 분석

   - 규칙 기반 의도 분류
   - 컨텍스트 기반 의도 파악
   - 다중 의도 처리

2. 라우팅

   - 적절한 에이전트 선택
   - 컨텍스트 전달
   - 상태 관리

3. 컨텍스트 관리
   - 대화 컨텍스트 유지
   - 세션 관리
   - 상태 추적

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── prompt_router/
│       ├── prompt_router_agent_executor.py
│       ├── prompt_router_agent_graph.py
│       ├── nodes/
│       │   └── input_node.py
│       ├── intent/
│       │   ├── manager.py
│       │   └── patterns.py
│       └── constants/
│           └── intent_constants.py
└── services/
    └── session/
        └── session_manage_service.py
```

## 사용 방법

### 1. 의도 분석 및 라우팅

```python
from tripmind.agents.prompt_router.prompt_router_agent_executor import PromptRouterAgentExecutor

router_agent = PromptRouterAgentExecutor()
result = router_agent.process_prompt(
    prompt="서울 여행 일정을 만들어줘",
    session_id="user_session_1",
    start_node="input_node"
)
```

### 2. 의도 패턴 관리

```python
from tripmind.agents.prompt_router.intent.manager import intent_pattern_manager

intent = intent_pattern_manager.determine_intent_by_rule_based(user_input)
```

## 상태 관리

```python
class PromptRouterState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    context: Optional[Dict[str, Any]]
```

## 개선이 필요한 부분

1. **의도 분석**

   - ML 기반 의도 분석 추가 필요
   - 의도 패턴 확장 필요
   - 다중 의도 처리 강화 필요

2. **에러 처리**

   - 구체적인 예외 타입 정의 필요
   - 에러 복구 메커니즘 구현 필요

3. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

4. **문서화**

   - API 문서화 필요
   - 코드 주석 보강 필요

5. **성능 최적화**

   - 의도 분석 성능 개선 필요
   - 라우팅 로직 최적화 필요

6. **확장성**
   - 새로운 에이전트 추가 용이성 개선 필요
   - 의도 패턴 관리 시스템 개선 필요
