from langchain.tools import Tool
from typing import List

from tripmind.services.place_search.base_place_search_service import PlaceSearchService

import logging

logger = logging.getLogger(__name__)


class PlaceSearchTool:
    def __init__(self, place_search_service: PlaceSearchService):
        self.place_search_service = place_search_service

    def search_places(self, query: str, location: str = None) -> str:
        """장소 검색 (도구 로직)"""
        print(f"검색 도구 호출됨: query={query}, location={location}")
        logger.debug(f"검색 도구 호출됨: query={query}, location={location}")
        try:
            places = self.place_search_service.search_places(query, location)

            if not places:
                return f"'{query}'에 대한 검색 결과가 없습니다."

            result = f"'{query}' 검색 결과:\n\n"
            for i, place in enumerate(places[:5], 1):  # 상위 5개만 표시
                result += f"{i}. {place['name']}\n"
                result += f"   주소: {place['address']}\n"
                result += f"   카테고리: {place['category']}\n"
                if place.get("phone"):
                    result += f"   전화: {place['phone']}\n"
                result += "\n"

            print(f"검색 결과: {result}")
            return result
        except Exception as e:
            print(f"장소 검색 중 오류가 발생했습니다: {str(e)}")
            return f"장소 검색 중 오류가 발생했습니다: {str(e)}"

    def get_place_details(self, place_id: str) -> str:
        """장소 상세 정보 조회 (도구 로직)"""
        try:
            place = self.place_search_service.get_place_details(place_id)

            if not place:
                return f"ID '{place_id}'에 대한 장소 정보를 찾을 수 없습니다."

            result = f"'{place['name']}' 상세 정보:\n\n"
            result += f"주소: {place['address']}\n"
            result += f"카테고리: {place['category']}\n"
            if place.get("phone"):
                result += f"전화: {place['phone']}\n"
            result += f"URL: {place['url']}\n"

            return result
        except Exception as e:
            return f"장소 정보 조회 중 오류가 발생했습니다: {str(e)}"

    def get_langchain_tools(self) -> List[Tool]:
        """LangChain 도구 리스트 반환"""
        return [
            Tool(
                name="SearchPlaces",
                func=self.search_places,
                description="Search for places by keyword. Optionally provide location as 'latitude,longitude'.",
            ),
            Tool(
                name="GetPlaceDetails",
                func=self.get_place_details,
                description="Get detailed information about a place using its ID.",
            ),
        ]
