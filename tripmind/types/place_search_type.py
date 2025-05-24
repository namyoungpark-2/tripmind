from typing import Optional
from pydantic import BaseModel


class PlaceSearchResult(BaseModel):
    id: str
    name: str
    address: str
    category: str
    phone: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    url: Optional[str] = None
    road_address: Optional[str] = None
