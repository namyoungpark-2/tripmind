from datetime import datetime
from typing import Dict, Any, List

from tripmind.services.external.base_calendar_service import BaseCalendarService
from tripmind.clients.google_calendar_client import GoogleCalendarClient


class GoogleCalendarService(BaseCalendarService):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self):
        self.client = GoogleCalendarClient()

    def add_event(
        self,
        date: str,
        start_time: str,
        end_time: str,
        title: str,
        location: str,
        description: str,
    ) -> Dict[str, Any]:
        """캘린더에 이벤트 추가 (포트 메서드 구현)"""
        # 도메인 데이터를 클라이언트 형식으로 변환
        start_datetime = f"{date}T{start_time}:00"
        end_datetime = f"{date}T{end_time}:00"

        event_data = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_datetime, "timeZone": "Asia/Seoul"},
        }

        # 클라이언트 호출 및 결과 반환
        result = self.client.create_event(event_data)

        # 클라이언트 응답을 도메인 형식으로 변환
        return {
            "id": result.get("id"),
            "title": result.get("summary"),
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "location": result.get("location", ""),
            "link": result.get("htmlLink", ""),
        }

    def list_events(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """일정 기간의 이벤트 조회 (포트 메서드 구현)"""
        # 날짜 형식 변환
        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        # 클라이언트 호출
        raw_events = self.client.get_events(time_min, time_max)

        # 클라이언트 응답을 도메인 형식으로 변환
        events = []
        for event in raw_events:
            start = event.get("start", {}).get("dateTime", "")
            end = event.get("end", {}).get("dateTime", "")

            if start and end:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

                events.append(
                    {
                        "id": event.get("id"),
                        "title": event.get("summary", "제목 없음"),
                        "date": start_dt.date().isoformat(),
                        "start_time": start_dt.time().strftime("%H:%M"),
                        "end_time": end_dt.time().strftime("%H:%M"),
                        "location": event.get("location", ""),
                        "description": event.get("description", ""),
                    }
                )

        return events
