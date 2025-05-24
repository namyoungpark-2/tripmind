from langchain.tools import StructuredTool
from typing import List, Optional
from tripmind.services.place_search.base_place_search_service import PlaceSearchService
from tripmind.agents.itinerary.types.place_search_tool_type import (
    SearchPlacesInput,
    GetPlaceDetailsInput,
)
import logging

logger = logging.getLogger(__name__)


def get_place_search_tools(
    place_search_service: PlaceSearchService,
) -> List[StructuredTool]:
    def search_places(keyword: str, location: Optional[str] = None) -> str:
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
            return result
        except Exception as e:
            logger.error(f"장소 검색 중 오류: {str(e)}")
            return f"장소 검색 중 오류가 발생했습니다: {str(e)}"

    def get_place_details(place_name: str, x: str, y: str) -> str:
        try:
            logger.debug(
                f"상세 정보 도구 호출됨: place_name={place_name}, x={x}, y={y}"
            )
            place = place_search_service.get_place_details(place_name, x, y)
            if not place:
                return f"place_name '{place_name}'에 대한 장소 정보를 찾을 수 없습니다."

            result = f"'{place.name}' 상세 정보:\n\n"
            result += f"ID: {place.id}\n"
            result += f"주소: {place.address}\n"
            result += f"카테고리: {place.category}\n"
            if place.phone:
                result += f"전화: {place.phone}\n"
            result += f"URL: {place.url}\n"
            return result
        except Exception as e:
            logger.error(f"장소 상세 조회 중 오류: {str(e)}")
            return f"장소 정보 조회 중 오류가 발생했습니다: {str(e)}"

    return [
        StructuredTool.from_function(
            func=search_places,
            name="SearchPlaces",
            description=(
                "키워드 및 좌표(lat,lng)를 기반으로 장소를 검색합니다.\n"
                "반드시 자연어를 제외한 입력 형식(JSON):\n"
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
        ),
        StructuredTool.from_function(
            func=get_place_details,
            name="GetPlaceDetails",
            description=(
                "장소 이름과 좌표를 기반으로 상세 정보를 조회합니다.\n"
                "반드시 자연어를 제외한 입력 형식(JSON):\n"
                "{\n"
                '  "place_name": "검색할 장소 이름 (예: 경복궁)",\n'
                '  "x": "37.5704",\n'
                '  "y": "126.9768"\n'
                "}\n"
                "예시:\n"
                "{\n"
                '  "place_name": "경복궁",\n'
                '  "x": "37.5704",\n'
                '  "y": "126.9768"\n'
                "}\n"
                "※ 중요 반드시 그 어떤 자연어 설명 포함 없이 반드시 위와 같은 JSON 형식으로 입력하며, JSON만 출력하세요."
            ),
            args_schema=GetPlaceDetailsInput,
        ),
    ]
