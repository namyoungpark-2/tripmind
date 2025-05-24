from typing import List
from tripmind.types.place_search_type import PlaceSearchResult


def format_place_result(place: PlaceSearchResult, index: int) -> str:
    result = f"{index}. **{place.name}** ({place.category})\n"
    result += f"   - 주소: {place.address}\n"
    if place.phone:
        result += f"   - 전화: {place.phone}\n"
    return result


def format_places_results(places: List[PlaceSearchResult]) -> str:
    if not places:
        return "검색 결과가 없습니다."

    return "\n".join(
        format_place_result(place, i) for i, place in enumerate(places[:5], 1)
    )
