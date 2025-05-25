from langchain.tools import StructuredTool
from typing import List, Optional
from tripmind.services.place_search.base_place_search_service import PlaceSearchService
from tripmind.agents.itinerary.types.place_search_tool_type import (
    SearchPlacesInput,
)
import logging

logger = logging.getLogger(__name__)

search_cache = {}


def get_place_search_tools(
    place_search_service: PlaceSearchService,
) -> List[StructuredTool]:
    def search_places(keyword: str, location: Optional[str] = None) -> str:
        cache_key = f"{keyword}_{location}"
        if cache_key in search_cache:
            return (
                f"[이전 검색 결과 사용] '{keyword}'에 대한 검색은 이미 수행되었습니다.\n"
                f"{search_cache[cache_key]}\n\n"
                "⚠️ 도구 호출 중단 조건에 도달했습니다. 지금 바로 FinalResponse 도구로 사용자에게 응답을 생성하세요."
            )

        try:
            logger.debug(f"검색 도구 호출됨: query={keyword}, location={location}")
            places = place_search_service.search_places(keyword, location)
            if not places:
                return f"'{keyword}'에 대한 검색 결과가 없습니다."

            result = f"'{keyword}' 검색 결과:\n\n"
            for i, place in enumerate(places[:5], 1):
                result += f"{i}. {place.name}\n"
                result += f"   ID: {place.id}\n"
                result += f"   주소: {place.address}\n"
                result += f"   카테고리: {place.category}\n"
                if place.phone:
                    result += f"   전화: {place.phone}\n"
                result += "\n"

            search_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"장소 검색 중 오류: {str(e)}")
            return f"장소 검색 중 오류가 발생했습니다: {str(e)}"

    return [
        StructuredTool.from_function(
            func=search_places,
            name="SearchPlaces",
            description=(
                "키워드 및 좌표(lat,lng)를 기반으로 장소를 검색합니다.\n"
                "반드시 자연어를 제외한 입력 형식(JSON):\n"
                "동일한 도구는 3번 이상 사용을 절대 금지합니다.\n"
                "{\n"
                '  "keyword": "검색할 키워드 (예: 경복궁)",\n'
                '  "location": "37.5704,126.9768"  // 생략 가능\n'
                "}\n"
                "예시:\n"
                "{\n"
                '  "keyword": "카페",\n'
                '  "location": "37.5665,126.9780"\n'
                "}\n"
                "※ 중요 반드시 그 어떤 자연어 설명 포함 없이 반드시 위와 같은 JSON 형식으로 입력하며, JSON만 출력하세요."
            ),
            args_schema=SearchPlacesInput,
        )
    ]
