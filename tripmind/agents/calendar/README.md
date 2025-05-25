# Calendar Agent

## 개요

Calendar Agent는 여행 일정을 Google Calendar와 연동하여 관리하는 에이전트입니다. 일정을 캘린더에 추가하고 조회하는 기능을 제공합니다.

## 주요 기능

1. 일정 캘린더 추가

   - 여행 일정을 Google Calendar에 자동으로 추가
   - 일정의 제목, 날짜, 시간, 장소 정보 포함

2. 일정 조회
   - 특정 기간의 캘린더 일정 조회
   - 일정 상세 정보 확인

## 아키텍처 구조

```
tripmind/
├── agents/
│   └── calendar/
│       ├── calendar_agent_executor.py
│       ├── calendar_agent_graph.py
│       ├── nodes/
│       │   └── calendar_node.py
│       └── types/
│           └── calendar_state_type.py
├── clients/
│   └── calendar/
│       ├── base_calendar_client.py
│       └── google_calendar_client.py
└── services/
    └── calendar/
        ├── base_calendar_service.py
        └── google_calendar_service.py
```

## 사용 방법

### 1. 환경 설정

```bash
# .env 파일에 다음 환경 변수 설정
GOOGLE_CALENDAR_ID=your_calendar_id
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json
```

### 2. 캘린더 일정 추가

```python
from tripmind.agents.calendar.calendar_agent_executor import CalendarRouterAgentExecutor

calendar_agent = CalendarRouterAgentExecutor()
result = calendar_agent.process_prompt(
    prompt="일정을 캘린더에 추가해주세요. id가 1, 2, 3",
    session_id="user_session_1"
)
```

### 3. 캘린더 일정 조회

```python
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient

calendar_service = GoogleCalendarService(
    GoogleCalendarClient(
        calendar_id=os.getenv("GOOGLE_CALENDAR_ID"),
        config_path=os.getenv("GOOGLE_CREDENTIALS_PATH")
    )
)

events = calendar_service.list_events(
    start_date="2024-03-01",
    end_date="2024-03-31"
)
```

## 개선이 필요한 부분

1. **에러 처리 및 로깅**

   - 구체적인 예외 타입 정의 필요
   - 로깅 레벨 및 포맷 표준화 필요

2. **테스트 코드**

   - 단위 테스트 추가 필요
   - 통합 테스트 추가 필요

3. **보안**
   - 인증 정보 관리 강화 필요
   - 보안 설정 중앙화 필요
