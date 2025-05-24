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
        self.api_key = api_key
        if self.api_key:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            logger.info(f"[DEBUG] Using Kakao API Key: {masked_key}")
        else:
            logger.error("[ERROR] 카카오 API 키가 설정되지 않았습니다.")
            raise ValueError("카카오 API 키가 설정되지 않았습니다.")

        self.headers = {"Authorization": f"KakaoAK {self.api_key}"}

    def search_keyword(
        self, keyword: str, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        url = f"{KAKAO_BASE_URL}/search/keyword.json"
        params = {"query": keyword, "page": page, "size": size}

        try:
            print(f"kakao request: {url}, {self.headers}, {params}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Kakao API request failed: {str(e)}")
            return {"documents": []}

    def search_category(
        self, category_group_code: str, x: str, y: str, radius: int = 1000
    ) -> Dict[str, Any]:
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
        url = f"{KAKAO_BASE_URL}/search/address.json"
        params = {"query": address}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_place_detail(self, place_name: str, x: str, y: str) -> Dict[str, Any]:
        url = f"{KAKAO_BASE_URL}/search/keyword.json"
        params = {
            "query": place_name,
            "x": x,
            "y": y,
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
