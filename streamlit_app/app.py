import streamlit as st
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import uuid

# 환경 변수 로드
load_dotenv()

# Django REST API URL
API_URL = "http://127.0.0.1:8000/api/tripmind/itinerary/"  # Django 서버 URL 조정 필요

# 앱 제목 설정
st.set_page_config(page_title="TripMind - 여행 에이전트", page_icon="✈️")
st.title("✈️ TripMind 여행 에이전트")

# 세션 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("여행 계획에 대해 물어보세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(prompt)

    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})

    # API 요청 준비
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": st.session_state.session_id,  # 세션 ID 포함
    }

    # 대화 히스토리를 포함한 요청 데이터 준비
    data = {
        "message": prompt,
        "history": st.session_state.messages[:-1],  # 방금 추가한 메시지 제외한 히스토리
    }

    # API 호출
    with st.spinner("응답 생성 중..."):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))

            # 응답 처리
            if response.status_code == 200:
                response_data = response.json()

                # 새로운 응답 구조 처리
                assistant_content = ""

                # 응답 형식 확인
                if "response" in response_data:
                    # 실패한 경우
                    if response_data["response"] == "응답을 생성하지 못했습니다.":
                        # messages 배열에서 마지막 assistant 메시지 찾기
                        if "messages" in response_data and response_data["messages"]:
                            for msg in response_data["messages"]:
                                if msg.get("role") == "assistant":
                                    assistant_content = msg.get("content", "")
                    else:
                        # 정상 응답
                        assistant_content = response_data["response"]
                elif "result" in response_data:
                    # 원래 예상했던 형식
                    assistant_content = response_data["result"]

                # 응답 내용이 없으면 기본 메시지
                if not assistant_content:
                    assistant_content = (
                        "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
                    )

                # 응답 표시
                with st.chat_message("assistant"):
                    st.write(assistant_content)

                # 응답 저장
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_content}
                )

                # 컨텍스트 정보 표시 (있는 경우)
                if "context" in response_data and response_data["context"]:
                    context = response_data["context"]
                    with st.sidebar:
                        st.subheader("여행 정보")
                        for key, value in context.items():
                            if value:
                                st.write(f"**{key}:** {value}")
            else:
                st.error(f"API 오류: {response.status_code} - {response.text}")
                st.write("API 응답:", response.text)
        except Exception as e:
            st.error(f"요청 오류: {str(e)}")

# 사이드바 정보
with st.sidebar:
    st.subheader("TripMind 사용 팁")
    st.markdown(
        """
    1. **여행지 정보 질문**: "바르셀로나에 대해 알려주세요"
    2. **여행 계획 요청**: "도쿄로 3박 4일 여행 계획 세워줘"
    3. **예산 고려**: "예산 50만원으로 제주도 여행"
    4. **특정 요구사항**: "아이와 함께하는 부산 여행 코스"
    """
    )

    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.session_id = (
            f"streamlit_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        st.experimental_rerun()

# 디버그 정보
if st.checkbox("디버그 정보 표시"):
    st.subheader("디버그 정보")
    st.write(f"세션 ID: {st.session_state.session_id}")
    st.write(f"메시지 수: {len(st.session_state.messages)}")

    if st.session_state.messages:
        st.json(st.session_state.messages)

    # API 요청/응답 확인용
    if st.button("API 응답 테스트"):
        try:
            test_headers = {
                "Content-Type": "application/json",
                "X-Session-ID": st.session_state.session_id,
            }
            test_data = {
                "message": "테스트 메시지",
                "history": st.session_state.messages,
            }
            test_response = requests.post(
                API_URL, headers=test_headers, data=json.dumps(test_data)
            )
            st.write("API 응답 코드:", test_response.status_code)
            st.json(test_response.json())
        except Exception as e:
            st.error(f"테스트 요청 오류: {str(e)}")
