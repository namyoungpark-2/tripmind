from typing import Dict, Any
import re
import logging
from datetime import datetime, timedelta
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from tripmind.agents.tools.calendar_tool import CalendarTool

logger = logging.getLogger(__name__)

# 캘린더 도구 초기화 (오류 처리 추가)
try:
    calendar_tool = CalendarTool()
    calendar_available = True
except Exception as e:
    logger.warning(f"캘린더 도구 초기화 실패: {str(e)}")
    calendar_available = False
    calendar_tool = None

def extract_date_info(text: str) -> Dict[str, str]:
    """
    텍스트에서 날짜 및 시간 정보 추출
    """
    result = {}
    
    # 날짜 추출 (YYYY-MM-DD 또는 MM/DD, 또는 '오늘', '내일', '모레' 등)
    date_pattern = r'(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}|\d{1,2}월\s*\d{1,2}일)'
    date_matches = re.findall(date_pattern, text)
    
    # 상대적 날짜 확인
    if not date_matches:
        if "오늘" in text:
            result["date"] = datetime.now().strftime("%Y-%m-%d")
        elif "내일" in text:
            result["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "모레" in text:
            result["date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # 첫 번째 날짜 포맷 변환
        date_str = date_matches[0]
        if "/" in date_str:
            month, day = date_str.split("/")
            result["date"] = f"{datetime.now().year}-{month.zfill(2)}-{day.zfill(2)}"
        elif "월" in date_str:
            month, day = date_str.split("월")
            day = day.replace("일", "").strip()
            result["date"] = f"{datetime.now().year}-{month.strip().zfill(2)}-{day.strip().zfill(2)}"
        else:
            result["date"] = date_str
    
    # 시작 시간 추출 (HH:MM 또는 H시 M분)
    start_time_pattern = r'(\d{1,2}:\d{2}|\d{1,2}시\s*\d{0,2}분?)'
    start_time_matches = re.findall(start_time_pattern, text)
    
    if start_time_matches:
        time_str = start_time_matches[0]
        if "시" in time_str:
            hour = time_str.split("시")[0].strip()
            minute = "00"
            if "분" in time_str:
                minute = time_str.split("시")[1].replace("분", "").strip() or "00"
            result["start_time"] = f"{hour.zfill(2)}:{minute.zfill(2)}"
        else:
            result["start_time"] = time_str
    
    # 종료 시간 추출 (start_time 이후의 시간)
    if start_time_matches and len(start_time_matches) > 1:
        time_str = start_time_matches[1]
        if "시" in time_str:
            hour = time_str.split("시")[0].strip()
            minute = "00"
            if "분" in time_str:
                minute = time_str.split("시")[1].replace("분", "").strip() or "00"
            result["end_time"] = f"{hour.zfill(2)}:{minute.zfill(2)}"
        else:
            result["end_time"] = time_str
    elif "start_time" in result:
        # 기본 종료 시간: 시작 시간 + 1시간
        start_hour, start_minute = map(int, result["start_time"].split(":"))
        end_hour = start_hour + 1
        result["end_time"] = f"{str(end_hour).zfill(2)}:{str(start_minute).zfill(2)}"
    
    # 일정 제목 추출
    title_patterns = [
        r'제목[은는:]?\s*["\']?([^"\']+)["\']?',
        r'일정[은는:]?\s*["\']?([^"\']+)["\']?',
        r'주제[는은:]?\s*["\']?([^"\']+)["\']?'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, text)
        if title_match:
            result["title"] = title_match.group(1).strip()
            break
    
    # 장소 추출
    location_match = re.search(r'장소[는은:]?\s*["\']?([^"\']+)["\']?', text)
    if location_match:
        result["location"] = location_match.group(1).strip()
    
    return result

def extract_date_range(text: str) -> Dict[str, str]:
    """
    텍스트에서 날짜 범위 추출
    """
    result = {}
    
    # 날짜 추출 (YYYY-MM-DD 또는 MM/DD, 또는 '오늘', '내일', '이번 주', '이번 달' 등)
    date_pattern = r'(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}|\d{1,2}월\s*\d{1,2}일)'
    date_matches = re.findall(date_pattern, text)
    
    today = datetime.now()
    
    # 특정 기간 확인
    if "이번 주" in text or "이번주" in text:
        # 이번 주 월요일부터 일요일까지
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        result["start_date"] = start_of_week.strftime("%Y-%m-%d")
        result["end_date"] = end_of_week.strftime("%Y-%m-%d")
    elif "이번 달" in text or "이번달" in text:
        # 이번 달 1일부터 말일까지
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        result["start_date"] = start_of_month.strftime("%Y-%m-%d")
        result["end_date"] = end_of_month.strftime("%Y-%m-%d")
    elif "오늘" in text:
        # 오늘 하루
        result["start_date"] = today.strftime("%Y-%m-%d")
        result["end_date"] = today.strftime("%Y-%m-%d")
    elif "내일" in text:
        # 내일 하루
        tomorrow = today + timedelta(days=1)
        result["start_date"] = tomorrow.strftime("%Y-%m-%d")
        result["end_date"] = tomorrow.strftime("%Y-%m-%d")
    elif len(date_matches) >= 2:
        # 두 개의 날짜가 명시적으로 있을 경우
        date1 = date_matches[0]
        date2 = date_matches[1]
        
        # 날짜 포맷 변환
        for date_str in [date1, date2]:
            if "/" in date_str:
                month, day = date_str.split("/")
                date_str = f"{today.year}-{month.zfill(2)}-{day.zfill(2)}"
            elif "월" in date_str:
                month, day = date_str.split("월")
                day = day.replace("일", "").strip()
                date_str = f"{today.year}-{month.strip().zfill(2)}-{day.strip().zfill(2)}"
        
        # 시작일과 종료일 결정 (시간순으로)
        if date1 <= date2:
            result["start_date"] = date1
            result["end_date"] = date2
        else:
            result["start_date"] = date2
            result["end_date"] = date1
    elif len(date_matches) == 1:
        # 하나의 날짜만 있을 경우, 해당 날짜 하루를 범위로 설정
        date_str = date_matches[0]
        if "/" in date_str:
            month, day = date_str.split("/")
            date_str = f"{today.year}-{month.zfill(2)}-{day.zfill(2)}"
        elif "월" in date_str:
            month, day = date_str.split("월")
            day = day.replace("일", "").strip()
            date_str = f"{today.year}-{month.strip().zfill(2)}-{day.strip().zfill(2)}"
        
        result["start_date"] = date_str
        result["end_date"] = date_str
    else:
        # 기본값: 오늘부터 일주일
        result["start_date"] = today.strftime("%Y-%m-%d")
        result["end_date"] = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    return result

def detect_calendar_intent(text: str) -> str:
    """
    텍스트에서 캘린더 관련 의도 탐지
    """
    # 일정 추가 의도
    add_patterns = [
        r'일정[을를]?\s*추가',
        r'일정[을를]?\s*등록',
        r'캘린더에\s*추가',
        r'캘린더에\s*일정',
        r'스케줄[을를]?\s*추가',
        r'미팅[을를]?\s*잡아',
        r'약속[을를]?\s*등록',
        r'예약[을를]?\s*등록'
    ]
    
    for pattern in add_patterns:
        if re.search(pattern, text):
            return "add_event"
    
    # 일정 조회 의도
    list_patterns = [
        r'일정[을를]?\s*보여',
        r'일정[을를]?\s*조회',
        r'일정[이가]?\s*뭐',
        r'일정[을를]?\s*확인',
        r'스케줄[을를]?\s*확인',
        r'캘린더\s*확인',
        r'약속[이가]?\s*뭐',
        r'일정[이가]?\s*있'
    ]
    
    for pattern in list_patterns:
        if re.search(pattern, text):
            return "list_events"
    
    # 기본 의도
    return "unknown"

def calendar_node(llm: ChatAnthropic, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    캘린더 노드 - 캘린더 일정 추가 및 조회 기능 제공
    """
    try:
        # 사용자 입력 가져오기
        user_input = state.get("user_input", "")
        messages = state.get("messages", [])
        context = state.get("context", {})
        
        # 캘린더 서비스 이용 불가능한 경우
        if not calendar_available:
            response_text = "죄송합니다. 현재 캘린더 서비스를 이용할 수 없습니다. 서비스 계정 설정을 확인해주세요."
            
            if "messages" not in state:
                state["messages"] = []
                
            state["messages"].append({"role": "assistant", "content": response_text})
            return {**state, "response": response_text}
        
        # 캘린더 관련 의도 탐지
        intent = detect_calendar_intent(user_input)
        
        # 의도에 따른 처리
        if intent == "add_event":
            # 일정 추가 처리
            date_info = extract_date_info(user_input)
            
            # 필수 정보가 부족한 경우 LLM 활용
            if not date_info.get("title"):
                prompt = ChatPromptTemplate.from_template(
                    """사용자가 일정을 추가하려고 합니다. 다음 메시지에서 일정 제목을 추출해주세요.
                    만약 명확한 제목이 없다면, 메시지 내용을 바탕으로 적절한: 제목을 생성해주세요.
                    
                    사용자 메시지: {message}
                    
                    제목:"""
                )
                
                # LLM 호출
                title_response = llm.invoke(prompt.format(message=user_input))
                date_info["title"] = title_response.content.strip()
            
            # 일정 추가 실행
            response_text = calendar_tool.add_calendar_event(
                date=date_info.get("date", datetime.now().strftime("%Y-%m-%d")),
                start_time=date_info.get("start_time", "09:00"),
                end_time=date_info.get("end_time", "10:00"),
                title=date_info.get("title", "새 일정"),
                location=date_info.get("location", ""),
                description=user_input  # 원래 메시지를 설명으로 사용
            )
            
        elif intent == "list_events":
            # 일정 조회 처리
            date_range = extract_date_range(user_input)
            
            # 일정 조회 실행
            response_text = calendar_tool.list_calendar_events(
                start_date=date_range.get("start_date"),
                end_date=date_range.get("end_date")
            )
            
        else:
            # 알 수 없는 의도
            response_text = "캘린더 기능을 사용하시려면 일정 추가나 조회에 관련된 요청을 해주세요. 예를 들어, '내일 오후 3시에 미팅 일정 추가해줘' 또는 '이번 주 일정 보여줘'와 같이 말씀해주세요."
        
        # 상태 업데이트
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append({"role": "assistant", "content": response_text})
        
        # 컨텍스트에 캘린더 관련 정보 저장
        if intent == "add_event":
            context["last_calendar_action"] = "add_event"
            context["last_calendar_event"] = {
                "date": date_info.get("date"),
                "title": date_info.get("title"),
                "start_time": date_info.get("start_time"),
                "end_time": date_info.get("end_time"),
            }
        elif intent == "list_events":
            context["last_calendar_action"] = "list_events"
            context["last_calendar_range"] = {
                "start_date": date_range.get("start_date"),
                "end_date": date_range.get("end_date"),
            }
        
        return {**state, "context": context, "response": response_text}
        
    except Exception as e:
        logger.error(f"캘린더 처리 오류: {str(e)}")
        logger.exception("전체 오류:")
        
        error_message = f"캘린더 기능 실행 중 오류가 발생했습니다: {str(e)}"
        
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append({"role": "assistant", "content": error_message})
        
        return {**state, "response": error_message} 