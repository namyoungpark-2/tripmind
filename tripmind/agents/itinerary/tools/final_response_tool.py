from tripmind.agents.itinerary.types.final_response_tool_type import (
    FinalResponseInput,
    FinalResponseListInput,
)
from langchain.tools import StructuredTool
from django.contrib.auth.models import User
from tripmind.models.itinerary import Itinerary
import json
from datetime import datetime
from django.utils.timezone import make_aware
from typing import List


def final_response_tool_fn(items: List[FinalResponseInput]) -> str:
    default_user = User.objects.get(id=1)
    responses = []

    for day in items:
        activities_json = json.dumps(
            [activity.model_dump() for activity in day.activities]
        )
        tips_json = json.dumps(day.tips or [])
        naive_dt = datetime.strptime(day.date, "%Y-%m-%d")
        aware_dt = make_aware(naive_dt)
        Itinerary.objects.create(
            user=default_user,
            title=day.title,
            destination=day.destination,
            duration=day.duration,
            itinerary_plan=activities_json,
            preferences=tips_json,
            travelers=1,
            date=aware_dt,
        )
        # print("day : ", day)
        # print(responses, day.natural_text)
        responses.append(day.natural_text)
    return "\n\n".join(responses)


FinalResponseTool = StructuredTool.from_function(
    name="FinalResponse",
    description=(
        "사용자에게 최종 여행 일정을 자연스러운 문장으로 전달하는 툴입니다.\n\n"
        "이 툴은 LLM이 생성한 구조화된 여행 일정 정보를 바탕으로, 대화체로 된 전체 여행 일정을 출력합니다.\n"
        "필수 입력값은 title(일정 제목), destination(여행지), duration(여행 기간), activities(여행 활동 리스트)입니다.\n"
        "각 activity에는 시간, 장소 이름, 설명, 주소를 포함합니다.\n"
        "추가로 여행 팁(tips)을 포함할 수 있으며, optional입니다.\n\n"
        "입력 예시:\n"
        "{\n"
        '  "items": [\n'
        "{ \n"
        '  "title": "서울 1일 여행",\n'
        '  "destination": "서울",\n'
        '  "duration": "1일",\n'
        '  "date": "2025-05-25",\n'
        '  "activities": [\n'
        "    {\n"
        '      "time": "09:00",\n'
        '      "title": "경복궁 관람",\n'
        '      "description": "조선왕조의 법궁을 감상할 수 있는 장소입니다.",\n'
        '      "address": "서울 종로구 세종로 1-1"\n'
        "    },\n"
        "    {\n"
        '      "time": "14:00",\n'
        '      "title": "남산서울타워 방문",\n'
        '      "description": "서울의 전경을 감상할 수 있는 전망대입니다.",\n'
        '      "address": "서울 용산구 용산동2가 산 1-3"\n'
        "    }\n"
        "  ],\n"
        '  "tips": ["편한 신발을 착용하세요", "1일권 교통카드를 사용하세요"]\n'
        '  "natural_text": "안녕하세요! 서울 1일 여행 계획은 다음과 같습니다..."\n'
        "},\n"
        "{ \n"
        '  "title": "서울 1일 여행",\n'
        '  "destination": "서울",\n'
        '  "duration": "1일",\n'
        '  "date": "2025-05-26",\n'
        '  "activities": [\n'
        "    {\n"
        '      "time": "09:00",\n'
        '      "title": "경복궁 관람",\n'
        '      "description": "조선왕조의 법궁을 감상할 수 있는 장소입니다.",\n'
        '      "address": "서울 종로구 세종로 1-1"\n'
        "    },\n"
        "    {\n"
        '      "time": "14:00",\n'
        '      "title": "남산서울타워 방문",\n'
        '      "description": "서울의 전경을 감상할 수 있는 전망대입니다.",\n'
        '      "address": "서울 용산구 용산동2가 산 1-3"\n'
        "    }\n"
        "  ],\n"
        '  "tips": ["편한 신발을 착용하세요", "1일권 교통카드를 사용하세요"]\n'
        '  "natural_text": "안녕하세요! 서울 1일 여행 계획은 다음과 같습니다..."\n'
        "},\n"
        "  ]\n"
        "}\n"
        "이 툴은 위 JSON 입력을 바탕으로 최종 자연어 응답을 생성합니다."
    ),
    func=final_response_tool_fn,
    args_schema=FinalResponseListInput,
    return_direct=True,
)
