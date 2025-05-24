from typing import Optional, Dict


class PlaceInfo(Dict):
    location: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    mood: Optional[str] = None
    price_range: Optional[str] = None
    count: Optional[int] = None
