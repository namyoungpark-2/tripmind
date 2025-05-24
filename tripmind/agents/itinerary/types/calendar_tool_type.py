from pydantic import BaseModel, Field


class AddCalendarEventInput(BaseModel):
    date: str = Field(..., description="이벤트 날짜 (YYYY-MM-DD)")
    start_time: str = Field(..., description="시작 시간 (HH:MM)")
    end_time: str = Field(..., description="종료 시간 (HH:MM)")
    title: str = Field(..., description="일정 제목")
    location: str = Field("", description="장소 (선택)")
    description: str = Field("", description="설명 (선택)")


class ListCalendarEventsInput(BaseModel):
    start_date: str = Field(..., description="시작 날짜 (YYYY-MM-DD)")
    end_date: str = Field(..., description="종료 날짜 (YYYY-MM-DD)")
