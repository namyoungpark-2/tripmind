from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseCalendarClient(ABC):
    @abstractmethod
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_events(self, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        pass
