from datetime import datetime
from typing import Dict, Any, List
from datetime import timedelta
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient
from tripmind.services.calendar.base_calendar_service import BaseCalendarService
from tripmind.models.itinerary import Itinerary


class GoogleCalendarService(BaseCalendarService):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.client = calendar_client

    def add_itinerary_to_calendar(self, itinerary: Itinerary) -> Dict[str, Any]:
        return self.add_event(
            itinerary.date,
            itinerary.date,
            itinerary.date + timedelta(days=1),
            itinerary.title,
            itinerary.destination,
            "",
        )

    def add_event(
        self,
        date: str,
        start_time: str,
        end_time: str,
        title: str,
        location: str,
        description: str,
    ) -> Dict[str, Any]:
        start_datetime = f"{date}T{start_time}:00"
        end_datetime = f"{date}T{end_time}:00"

        event_data = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_datetime, "timeZone": "Asia/Seoul"},
        }

        print("event_data : ", event_data)
        result = self.client.create_event(event_data)

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
        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        raw_events = self.client.get_events(time_min, time_max)

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
