# Conversation Agent

## 개요

Conversation Agent는 사용자와의 자연스러운 대화를 처리하는 에이전트입니다. LLM(Large Language Model)을 활용하여 사용자의 입력에 대한 응답을 생성하고, 대화 기록을 관리합니다.

## 주요 기능

1. 대화 처리

   - 사용자 입력에 대한 자연스러운 응답 생성
   - LLM을 활용한 컨텍스트 기반 대화
   - 스트리밍 방식의 응답 전달

2. 대화 기록 관리

   - 세션 기반 대화 기록 저장
   - 대화 컨텍스트 유지
   - 대화 기록 조회 및 초기화

3. 노드 기반 처리

   - 라우터 노드: 대화 흐름 제어
   - 인사 노드: 초기 인사 처리
   - 대화 노드: 주요 대화 처리

4. 다중 LLM 지원
   - Claude (Anthropic)
   - Llama3 (Ollama)
   - 환경 변수를 통한 모델 설정
   - 의존성 주입을 통한 유연한 LLM 교체

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── conversation/
│       ├── conversation_agent_executor.py
│       ├── conversation_agent_graph.py
│       ├── nodes/
│       │   ├── conversation_node.py
│       │   ├── greeting_node.py
│       │   └── router_node.py
│       └── types/
│           └── conversation_state_type.py
├── clients/
│   └── llm/
│       ├── base_llm_client.py
│       ├── claude_client.py
│       └── ollama_client.py
├── services/
│   └── conversation/
│       └── conversation_history_service.py
└── models/
    └── session.py
```

## 사용 방법

### 1. 대화 처리

```python
from tripmind.agents.conversation.conversation_agent_executor import ConversationAgentExecutor
from tripmind.clients.llm.claude_client import ClaudeClient
from tripmind.clients.llm.ollama_client import OllamaClient

# Claude 사용
claude_agent = ConversationAgentExecutor(llm_client=ClaudeClient())
result = claude_agent.process_prompt(
    prompt="안녕하세요",
    session_id="user_session_1",
    start_node="greeting_node"
)

# Llama3 사용
llama_agent = ConversationAgentExecutor(llm_client=OllamaClient())
result = llama_agent.process_prompt(
    prompt="안녕하세요",
    session_id="user_session_1",
    start_node="greeting_node"
)
```

### 2. 대화 기록 관리

```python
from tripmind.services.conversation.conversation_history_service import ConversationHistoryService

# 대화 기록 조회
history = conversation_history_service.get_conversation_history(session)

# 대화 기록 초기화
conversation_history_service.clear_conversation(session)
```

## 상태 관리

```python
class ConversationState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    query: Optional[str]
    session_id: Optional[str]
    context: Optional[Dict[str, Any]]
    streaming: Optional[Dict[str, Any]]
```

## 개선이 필요한 부분

1. **에러 처리**

   - 구체적인 예외 타입 정의 필요
   - 에러 복구 메커니즘 구현 필요

2. **성능 최적화**

   - 스트리밍 응답 지연 시간 조정 필요
   - 메모리 사용량 최적화 필요

3. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

4. **문서화**

   - API 문서화 필요
   - 코드 주석 보강 필요

5. **보안**
   - 세션 관리 보안 강화 필요
   - 입력 데이터 검증 강화 필요
