# 🧭 TripMind Architecture Overview

## 📌 프로젝트 목표

- LLM 기반 멀티 에이전트를 활용하여 사용자와의 대화를 통해 **여행 일정을 생성**, **장소 검색**, **일정 관리(캘린더 연동)**, **일정 공유** 기능을 제공.
- LangChain + LangGraph를 이용한 **에이전트 기반 흐름 구성**
- Django와 DRF를 백엔드로 사용, Streamlit을 통한 독립 UI 제공
- 외부 API (카카오, 네이버) 활용 + LLM Guardrails 적용

---

## 🏗️ 아키텍처 다이어그램

```
                        ┌────────────┐
                        │  Streamlit │ ◄────────────┐
                        └────┬───────┘              │
                             │ UI 요청               │
                             ▼                       │
                    ┌─────────────────┐              │
                    │  LangGraph DAG  │              │
                    │ (에이전트 조합) │              │
                    └─────────────────┘              │
                      ▲      ▲      ▲                │
          ┌──────────┘      │      └────────────┐    │
          │                 │                   │    │
┌────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ SearchAgent     │ │ ItineraryAgent    │ │ CalendarAgent     │
└────────────────┘ └──────────────────┘ └──────────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
 ┌───────────────┐ ┌────────────────┐ ┌────────────────────┐
 │ Kakao API     │ │ PromptTemplate │ │ Naver Calendar API │
 │ Naver Search  │ │ LangChain Chain│ │ ICS 변환 등         │
 └───────────────┘ └────────────────┘ └────────────────────┘

        ▲
        │
┌────────────────────┐
│ itinerary_service.py │ ← 서비스 계층 (비즈니스 로직)
└────────────────────┘
        ▲
        │
┌───────────────────────┐
│   Django REST API     │ ← DRF (rest_api/, serializers/)
└───────────────────────┘
        ▲
        │
┌──────────────────────────┐
│ Django MVC               │ ← models/, views/, templates/
└──────────────────────────┘
```

---

## 📁 디렉토리 구조 설명

| 디렉토리          | 설명                                                                  |
| ----------------- | --------------------------------------------------------------------- |
| `agents/`         | LangGraph에서 사용하는 에이전트 정의 (search, itinerary, calendar 등) |
| `chains/`         | LangChain 체인 구성, Guardrails 포함                                  |
| `llms/`           | OpenAI 등 모델 래퍼 및 프롬프트 템플릿 관리                           |
| `services/`       | 비즈니스 로직 중심 서비스 계층                                        |
| `interfaces/ui/`  | Streamlit 기반 웹 UI 구성                                             |
| `interfaces/api/` | 카카오, 네이버 등 외부 API 연동 모듈                                  |
| `models/`         | Django ORM 모델 (Itinerary, Conversation, User 등)                    |
| `templates/`      | Django 템플릿 (웹 페이지용)                                           |
| `views/`          | Django 뷰 - 검색/일정/캘린더 등 처리                                  |
| `forms/`          | Django Forms (검색 폼, 일정 폼 등)                                    |
| `serializers/`    | DRF API용 직렬화 클래스                                               |
| `rest_api/`       | DRF API View + URL 구성                                               |
| `utils/`          | Guardrails, 예외처리, 기타 유틸리티                                   |
| `tests/`          | 모델/뷰/에이전트 테스트                                               |

---

## 🔐 기술적 고려 사항

### ✅ 거짓 정보 방지

- `guardrails_chain.py` 및 `guardrails.py`를 활용한 응답 필터링
- "모르는 건 모른다고 답하라"는 정책성 프롬프트 내장

### ✅ 확장성

- 프롬프트 템플릿을 파일 기반으로 관리 → 모델별 버전 대응 용이
- 모델 버전 및 LLM 소스(OpenAI, Anthropic 등) 교체가 가능하도록 래핑 구조
- LangGraph를 통한 멀티에이전트 흐름 재사용 및 확장 가능

### ✅ 장애 대응

- API Timeout, 인증 에러, 잘못된 입력 등은 `exceptions.py`로 커스텀 핸들링
- 외부 API 실패 시 fallback 메시지 제공

### ✅ 테스트

- Agent 유닛 테스트 (`test_agents.py`)
- 전체 플로우 통합 테스트 가능 (LangGraph 시뮬레이션)

---

## 📤 제출용 준비사항

- `.env` 키 제거 및 `config.py` 분리
- Streamlit UI 스크린샷 캡처
- README.md + 이 문서 포함

---

## 🏁 결론

> TripMind는 Django + LangChain + LangGraph + Streamlit을 결합한 **현대적인 멀티 에이전트 기반 여행 일정 생성기**이며, 헥사고날 아키텍처 철학과 클린 아키텍처의 모범 구현 사례입니다.
