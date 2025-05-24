from langchain.tools import StructuredTool
from typing import List
from tripmind.services.calendar.base_calendar_service import BaseCalendarService
from tripmind.agents.itinerary.types.calendar_tool_type import (
    AddCalendarEventInput,
    ListCalendarEventsInput,
)


def get_calendar_tools(calendar_service: BaseCalendarService) -> List[StructuredTool]:
    def add_calendar_event_func(
        date: str,
        start_time: str,
        end_time: str,
        title: str,
        location: str = "",
        description: str = "",
    ) -> str:
        try:
            result = calendar_service.add_event(
                date=date,
                start_time=start_time,
                end_time=end_time,
                title=title,
                location=location,
                description=description,
            )
            return f"일정이 성공적으로 추가되었습니다: {result['title']} ({date} {start_time}~{end_time})"
        except Exception as e:
            return f"일정 추가 중 오류가 발생했습니다: {str(e)}"

    def list_calendar_events_func(start_date: str, end_date: str) -> str:
        try:
            events = calendar_service.list_events(
                start_date=start_date,
                end_date=end_date,
            )
            if not events:
                return f"{start_date}부터 {end_date}까지 일정이 없습니다."

            result = f"{start_date}부터 {end_date}까지의 일정:\n\n"
            for i, event in enumerate(events, 1):
                result += f"{i}. {event['title']}\n"
                result += f"   일시: {event['date']} {event['start_time']}-{event['end_time']}\n"
                if event.get("location"):
                    result += f"   장소: {event['location']}\n"
                result += "\n"
            return result
        except Exception as e:
            return f"일정 조회 중 오류가 발생했습니다: {str(e)}"

    return [
        StructuredTool.from_function(
            func=add_calendar_event_func,
            name="AddCalendarEvent",
            description="캘린더에 새 일정을 추가합니다. Add a new event to the calendar. Input should be a JSON string with date (YYYY-MM-DD), start_time (HH:MM), end_time (HH:MM), title, and optionally location and description. Do not add any additional text after the JSON.",
            args_schema=AddCalendarEventInput,
        ),
        StructuredTool.from_function(
            func=list_calendar_events_func,
            name="ListCalendarEvents",
            description="지정한 날짜 범위 내의 일정을 조회합니다. List calendar events between start_date and end_date. Input should be a JSON string with start_date and end_date in YYYY-MM-DD format. Do not add any additional text after the JSON.",
            args_schema=ListCalendarEventsInput,
        ),
    ]
