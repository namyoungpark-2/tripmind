# tripmind/infrastructure/external/kakao/kakao_place_client.py
import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class KakaoPlaceClient:
    def __init__(self, ):
        # API 키 설정 및 검증
        self.api_key = os.getenv("KAKAO_REST_KEY") or '7582a0567cfa228ec8c38f2e3dafe03a'
        
        # 디버깅용: API 키 확인 (첫 4자와 마지막 4자만 표시)
        if self.api_key:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            logger.info(f"[DEBUG] Using Kakao API Key: {masked_key}")
        else:
            logger.error("[ERROR] 카카오 API 키가 설정되지 않았습니다.")
            raise ValueError("카카오 API 키가 설정되지 않았습니다.")
        
        self.base_url = "https://dapi.kakao.com/v2/local"
        self.headers = {"Authorization": f"KakaoAK {self.api_key}"}
        print("Headers:", self.headers)

    def search_keyword(self, keyword: str, page: int = 1, size: int = 15) -> Dict[str, Any]:
        """
        키워드로 장소 검색
        """
        url = f"{self.base_url}/search/keyword.json"
        params = {
            "query": keyword,
            "page": page,
            "size": size
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Kakao API request failed: {str(e)}")
            # 에러를 그대로 전파하지 않고 빈 결과 반환
            return {"documents": []}
    
    def search_category(self, category_group_code: str, 
                        x: str, y: str, radius: int = 1000) -> Dict[str, Any]:
        """
        카테고리로 장소 검색
        """
        url = f"{self.base_url}/search/category.json"
        params = {
            "category_group_code": category_group_code,
            "x": x,
            "y": y,
            "radius": radius
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def search_address(self, address: str) -> Dict[str, Any]:
        """
        주소로 좌표 검색
        """
        url = f"{self.base_url}/search/address.json"
        params = {"query": address}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_place_detail(self, place_id: str) -> Dict[str, Any]:
        """장소 상세 정보 API 호출 (로우레벨)"""
        url = f"{self.base_url}/search/category.json"
        params = {"category_group_code": place_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()