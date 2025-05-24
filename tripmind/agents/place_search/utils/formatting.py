from typing import List
from tripmind.types.place_search_type import PlaceSearchResult


def format_place_result(place: PlaceSearchResult, index: int) -> str:
    place_dict = place.model_dump()
    result = f"{index}. **{place_dict['name']}** ({place_dict['category']})\n"
    result += f"   - 주소: {place_dict['address']}\n"
    if place_dict.get("phone"):
        result += f"   - 전화: {place_dict['phone']}\n"
    return result


def format_places_results(places: List[PlaceSearchResult]) -> str:
    if not places:
        return "검색 결과가 없습니다."
    return "\n".join(
        format_place_result(place, i) for i, place in enumerate(places[:5], 1)
    )
