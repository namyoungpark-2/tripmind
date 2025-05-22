# tripmind/infrastructure/external/google/google_calendar_client.py
import os
from typing import Dict, Any, List
from google.oauth2 import service_account
from googleapiclient.discovery import build

project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'
))

# Google Calendar API 권한 범위
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """구글 캘린더 API 클라이언트 (로우레벨 인프라)"""
    
    def __init__(self):
        # 기본 서비스 계정 파일 경로 설정 (프로젝트 루트 기준)
        service_account_file = os.path.join(project_root, 'service-account.json')
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file or os.getenv("GOOGLE_CREDENTIALS_PATH"),
            scopes=SCOPES
        )
        self.service = build("calendar", "v3", credentials=credentials)
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """이벤트 생성 API 호출 (로우레벨)"""
        return self.service.events().insert(
            calendarId=self.calendar_id,
            body=event_data
        ).execute()
    
    def get_events(self, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        """이벤트 조회 API 호출 (로우레벨)"""
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events_result.get("items", [])