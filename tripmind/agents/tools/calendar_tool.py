from typing import List
from langchain.tools import Tool
from tripmind.services.external.base_calendar_service import BaseCalendarService
from tripmind.services.external.google_calendar_service import GoogleCalendarService


class CalendarTool:
    def __init__(self, calendar_service: BaseCalendarService = None):
        self.calendar_service = calendar_service or GoogleCalendarService()

    def add_calendar_event(
        self,
        date: str,
        start_time: str,
        end_time: str,
        title: str,
        location: str = "",
        description: str = "",
    ) -> str:
        """캘린더에 이벤트 추가 (도구 로직)"""
        try:
            result = self.calendar_service.add_event(
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

    def list_calendar_events(self, start_date: str, end_date: str) -> str:
        """일정 기간의 이벤트 조회 (도구 로직)"""
        try:
            events = self.calendar_service.list_events(start_date, end_date)

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

    def get_langchain_tools(self) -> List[Tool]:
        """LangChain 도구 리스트 반환"""
        return [
            Tool(
                name="AddCalendarEvent",
                func=self.add_calendar_event,
                description="Add a new event to the calendar. You should provide date (YYYY-MM-DD), start_time (HH:MM), end_time (HH:MM), title, and optionally location and description.",
            ),
            Tool(
                name="ListCalendarEvents",
                func=self.list_calendar_events,
                description="List calendar events between start_date and end_date. Both dates should be in YYYY-MM-DD format.",
            ),
        ]
