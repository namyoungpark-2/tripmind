# TripMind Streamlit 애플리케이션

TripMind 여행 에이전트 서비스를 위한 Streamlit 기반 웹 애플리케이션 입니다. 이 앱은 LangGraph 기반 여행 에이전트 API와 통신하여 사용자에게 여행 관련 정보와 일정을 제공합니다.

## 사전 요구사항

- Python 3.8 이상
- Django 백엔드 서버 실행 중 (LangGraphAPIView)
- 필요한 패키지들이 설치됨

## 설치 및 실행 방법

1. 필요한 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```

2. Django 백엔드 서버 실행:

   ```bash
   # 다른 터미널에서 실행
   cd /path/to/tripmind
   python manage.py runserver
   ```

3. Streamlit 앱 실행:

   ```bash
   cd /path/to/tripmind
   streamlit run streamlit_app.py
   ```

4. 브라우저에서 앱 접속:
   - 기본적으로 http://localhost:8501 에서 접속 가능합니다.

## 앱 사용법

1. 채팅 인터페이스에 여행 관련 질문을 입력합니다.

   - 예: "오사카에 대해 알려주세요"
   - 예: "서울로 2박 3일 여행 계획 세워줘"

2. 여행 일정이 생성되면 마크다운 형식으로 표시됩니다.

3. 여행 목적지와 기간 정보는 사이드바에 표시됩니다.

4. "대화 초기화" 버튼을 사용하여 새로운 대화를 시작할 수 있습니다.

## 문제 해결

- API 연결 오류가 발생하면 Django 서버가 실행 중인지 확인하세요.
- Django 서버 URL이 `API_URL` 변수의 값과 일치하는지 확인하세요.
- 실제 운영 환경에서는 CORS 설정을 적절히 구성해야 합니다.

## 추가 기능

- 세션 정보는 브라우저의 세션 스토리지에 저장됩니다.
- 각 세션은 고유한 ID를 가집니다.
- 사이드바에 유용한 사용 팁이 표시됩니다.

## 참고사항

- 실제 배포 시에는 API URL을 환경 변수로 설정하는 것이 좋습니다.
- 사용자 인증이 필요한 경우, 적절한 인증 로직을 추가해야 합니다.
