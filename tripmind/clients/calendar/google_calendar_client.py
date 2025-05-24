import os
from typing import Dict, Any, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from tripmind.clients.calendar.base_calendar_client import BaseCalendarClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarClient(BaseCalendarClient):

    def __init__(self, calendar_id: str, config_path: str):
        service_account_file = config_path
        self.calendar_id = calendar_id

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file or os.getenv("GOOGLE_CREDENTIALS_PATH"), scopes=SCOPES
        )
        self.service = build("calendar", "v3", credentials=credentials)

    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        result = (
            self.service.events()
            .insert(calendarId=self.calendar_id, body=event_data)
            .execute()
        )
        print(f"create_event result: {result}")
        return result

    def get_events(self, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
