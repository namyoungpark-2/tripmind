from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCalendarService(ABC):
    @abstractmethod
    def add_event(self, date: str, start_time: str, end_time: str, 
                 title: str, location: str, description: str) -> Dict[str, Any]:
        """캘린더에 이벤트 추가"""
        pass
    
    @abstractmethod
    def list_events(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """일정 기간의 이벤트 조회"""
        pass
