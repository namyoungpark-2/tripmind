from abc import ABC, abstractmethod
from typing import List, Optional

from tripmind.types.place_search_type import PlaceSearchResult


class PlaceSearchService(ABC):

    @abstractmethod
    def search_places(
        self, query: str, location: Optional[str] = None
    ) -> List[PlaceSearchResult]:
        pass

    @abstractmethod
    def get_place_details(self, place_name: str, x: str, y: str) -> PlaceSearchResult:
        pass
