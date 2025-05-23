# tripmind/infrastructure/external/kakao/kakao_place_client.py
import requests
import logging
from typing import Dict, Any

from tripmind.clients.place_search.base_place_search_client import BasePlaceSearchClient

logger = logging.getLogger(__name__)

KAKAO_BASE_URL = "https://dapi.kakao.com/v2/local"


class KakaoPlaceClient(BasePlaceSearchClient):
    def __init__(
        self,
        api_key: str,
    ):
        # API 키 설정 및 검증
        # self.api_key = os.getenv("KAKAO_REST_KEY")

        self.api_key = api_key
        # 디버깅용: API 키 확인 (첫 4자와 마지막 4자만 표시)
        if self.api_key:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            logger.info(f"[DEBUG] Using Kakao API Key: {masked_key}")
        else:
            logger.error("[ERROR] 카카오 API 키가 설정되지 않았습니다.")
            raise ValueError("카카오 API 키가 설정되지 않았습니다.")

        self.headers = {"Authorization": f"KakaoAK {self.api_key}"}

    def search_keyword(
        self, keyword: str, page: int = 1, size: int = 15
    ) -> Dict[str, Any]:
        """
        키워드로 장소 검색
        """
        url = f"{KAKAO_BASE_URL}/search/keyword.json"
        params = {"query": keyword, "page": page, "size": size}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Kakao API request failed: {str(e)}")
            return {"documents": []}

    def search_category(
        self, category_group_code: str, x: str, y: str, radius: int = 1000
    ) -> Dict[str, Any]:
        """
        카테고리로 장소 검색
        """
        url = f"{KAKAO_BASE_URL}/search/category.json"
        params = {
            "category_group_code": category_group_code,
            "x": x,
            "y": y,
            "radius": radius,
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def search_address(self, address: str) -> Dict[str, Any]:
        """
        주소로 좌표 검색
        """
        url = f"{KAKAO_BASE_URL}/search/address.json"
        params = {"query": address}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_place_detail(self, place_id: str) -> Dict[str, Any]:
        """장소 상세 정보 API 호출 (로우레벨)"""
        url = f"{KAKAO_BASE_URL}/search/category.json"
        params = {"category_group_code": place_id}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
