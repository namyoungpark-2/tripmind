from typing import List, Optional

from tripmind.services.place_search.base_place_search_service import PlaceSearchService
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient
from tripmind.types.place_search_type import PlaceSearchResult


class KakaoPlaceSearchService(PlaceSearchService):
    """
    Kakao 로컬 검색 API를 이용해 장소 검색을 수행하는 Adapter
    """

    def __init__(self, kakao_place_client: KakaoPlaceClient):
        self.client = kakao_place_client

    def search_places(
        self, query: str, location: Optional[str] = None, page: int = 1, size: int = 5
    ) -> List[PlaceSearchResult]:
        """장소 검색 (포트 메서드 구현)"""
        # 위치 정보 파싱 (있는 경우)
        x, y = None, None
        if location:
            parts = location.split(",")
            if len(parts) >= 2:
                x, y = parts[0].strip(), parts[1].strip()

        # 클라이언트 호출
        result = self.client.search_keyword(query, page=page, size=size)

        # 클라이언트 응답을 도메인 형식으로 변환
        places = []
        for place in result.get("documents", []):
            places.append(
                PlaceSearchResult(
                    id=place.get("id"),
                    name=place.get("place_name"),
                    address=place.get("address_name"),
                    category=place.get("category_name"),
                    phone=place.get("phone"),
                    x=place.get("x"),
                    y=place.get("y"),
                    url=place.get("place_url"),
                )
            )

        return places

    def search_places_detail(
        self, keyword: str, page: int = 1, size: int = 5
    ) -> List[PlaceSearchResult]:
        """
        키워드로 장소를 검색하여 상세 정보 목록을 반환
        """
        try:
            result = self.client.search_keyword(keyword, page=page, size=size)
            places = result.get("documents", [])

            formatted_places = []
            for place in places:
                formatted_places.append(
                    PlaceSearchResult(
                        id=place.get("id"),
                        name=place.get("place_name"),
                        category=place.get("category_name"),
                        address=place.get("address_name"),
                        road_address=place.get("road_address_name"),
                        phone=place.get("phone"),
                        url=place.get("place_url"),
                        x=place.get("x"),  # 경도
                        y=place.get("y"),  # 위도
                    )
                )

            return formatted_places

        except Exception as e:
            print(f"[Kakao API 오류] {str(e)}")
            return []

    def get_place_details(self, place_name: str, x: str, y: str) -> PlaceSearchResult:
        """장소 상세 정보 조회 (포트 메서드 구현)"""
        # 클라이언트 호출
        result = self.client.get_place_detail(place_name, x, y)

        # 상세 정보가 있을 경우
        if result.get("documents") and len(result["documents"]) > 0:
            place = result["documents"][0]
            return PlaceSearchResult(
                id=place.get("id"),
                name=place.get("place_name"),
                address=place.get("address_name"),
                category=place.get("category_name"),
                phone=place.get("phone"),
                x=place.get("x"),
                y=place.get("y"),
                url=place.get("place_url"),
            )

        return None
