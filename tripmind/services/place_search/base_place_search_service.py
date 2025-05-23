from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class PlaceSearchService(ABC):
    """장소 검색 서비스 포트 (출력 포트)"""

    @abstractmethod
    def search_places(
        self, query: str, location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """장소 검색"""
        pass

    @abstractmethod
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """장소 상세 정보 조회"""
        pass
