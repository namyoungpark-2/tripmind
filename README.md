# 🧭 TripMind - AI 기반 여행 일정 계획 멀티 에이전트

## 📌 프로젝트 개요

TripMind는 LLM 기반 멀티 에이전트를 활용하여 사용자와의 대화를 통해 여행 일정을 생성하고 관리하는 서비스입니다. 장소 검색, 일정 관리, 캘린더 연동, 일정 공유 등의 기능을 제공합니다.

## ✨ 주요 기능

1. **여행 일정 생성**

   - 목적지 기반 일정 추천
   - 장소 검색 및 상세 정보 조회
   - 일정 최적화 및 조정

2. **장소 검색**

   - 키워드 기반 장소 검색
   - 위치 기반 장소 검색
   - 카테고리별 장소 검색

3. **캘린더 연동**

   - Google Calendar 연동
   - 일정 자동 등록
   - 일정 조회 및 관리

4. **일정 공유**
   - 공유 링크 생성
   - 다양한 공유 방식 지원
   - 공유 권한 관리

## 🏗️ 기술 스택

### 백엔드

- Django + DRF
- LangChain + LangGraph
- PostgreSQL

### 프론트엔드

- Streamlit

### 외부 서비스

- Anthropic Claude
- Ollama (Llama3)
- Kakao API
- Google Calendar API

## 🎯 아키텍처

### 레이어드 아키텍처

```
tripmind/
├── agents/          # 에이전트 계층
├── services/        # 서비스 계층
├── clients/         # 외부 API 클라이언트
├── models/          # 데이터 모델
└── api/            # API 엔드포인트
```

### 에이전트 구조

- Prompt Router Agent: 사용자 입력 분석 및 라우팅
- Conversation Agent: 일반 대화 처리
- Itinerary Agent: 여행 일정 생성
- Place Search Agent: 장소 검색
- Calendar Agent: 캘린더 연동
- Sharing Agent: 일정 공유

## 🚀 시작하기

### 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 필요한 API 키 설정
```

### 서버 실행

```bash
# Django 서버
python manage.py runserver

# Streamlit UI
streamlit run streamlit_app/app.py
```

## 🔒 보안

- API 키는 환경 변수로 관리
- 사용자 인증 및 권한 관리
- 입력 데이터 검증
- LLM 가드레일 적용

## 🧪 테스트

```bash
# 단위 테스트
python manage.py test

# 통합 테스트
python manage.py test tests/integration
```

## 📚 문서

- [아키텍처 문서](architecture.md)
- [API 문서](api/README.md)
- [에이전트 문서](agents/README.md)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- Anthropic의 Claude API
- Kakao의 장소 검색 API
- Google Calendar API
- LangChain & LangGraph 팀
