from pydantic import BaseModel, Field
from typing import Optional


class SearchPlacesInput(BaseModel):
    keyword: str = Field(..., description="검색할 장소 키워드 (예: 경복궁)")
    location: Optional[str] = Field(None, description="검색 중심 좌표 (lat,lng) 형식")


class GetPlaceDetailsInput(BaseModel):
    id: str = Field(..., description="장소의 고유 ID")
