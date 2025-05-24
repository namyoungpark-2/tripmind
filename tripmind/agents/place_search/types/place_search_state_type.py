from typing import Optional, List, Dict
from tripmind.agents.common.types.base_state_type import BaseState
from tripmind.types.place_search_type import PlaceSearchResult


class LastSearch(Dict):
    query: str
    location: Optional[str] = None
    results: List[PlaceSearchResult] = []


class PlaceSearchContext(Dict):
    last_search: Optional[LastSearch] = None


class PlaceSearchState(BaseState):
    parsed_info: Dict[str, str]
