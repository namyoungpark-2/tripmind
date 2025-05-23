from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePlaceSearchClient(ABC):
    @abstractmethod
    def search_keyword(
        self, keyword: str, page: int = 1, size: int = 15
    ) -> Dict[str, Any]:
        """키워드로 장소 검색"""
        pass

    @abstractmethod
    def search_category(
        self, category_group_code: str, x: str, y: str, radius: int = 1000
    ) -> Dict[str, Any]:
        """카테고리로 장소 검색"""
        pass

    @abstractmethod
    def search_address(self, address: str) -> Dict[str, Any]:
        """주소로 장소 검색"""
        pass

    @abstractmethod
    def get_place_detail(self, place_id: str) -> Dict[str, Any]:
        """장소 상세 정보 조회"""
        pass
