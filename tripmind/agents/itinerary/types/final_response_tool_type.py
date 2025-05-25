from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ItineraryActivity(BaseModel):
    time: str
    title: str
    description: str
    address: Optional[str] = None


class ItineraryBase(BaseModel):
    title: str
    destination: str
    duration: str
    travelers: int = 1
    budget: Optional[str] = ""
    preferences: Optional[str] = ""
    special_requirements: Optional[str] = ""
    itinerary_plan: str


class ItineraryCreate(ItineraryBase):
    pass


class ItineraryResponse(ItineraryBase):
    id: int
    user_id: int
    share_id: UUID
    is_public: bool
    share_type: str
    share_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SharedItineraryBase(BaseModel):
    itinerary_id: int
    shared_with_id: int
    can_edit: bool = False


class SharedItineraryCreate(SharedItineraryBase):
    pass


class SharedItineraryResponse(SharedItineraryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ActivityItem(BaseModel):
    time: str = Field(..., example="09:00")
    title: str = Field(..., example="경복궁 관람")
    description: str = Field(..., example="조선왕조의 법궁을 감상")
    address: Optional[str] = Field(None, example="서울 종로구 세종로 1-1")


class FinalResponseInput(BaseModel):
    title: str
    destination: str
    duration: str
    date: str
    activities: List[ActivityItem]
    tips: Optional[List[str]] = []
    natural_text: Optional[str] = ""


class FinalResponseListInput(BaseModel):
    items: List[FinalResponseInput]
