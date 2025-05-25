import logging
import re

from tripmind.agents.calendar.types.calendar_state_type import CalendarState
from tripmind.models.itinerary import Itinerary
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


def calendar_node(
    state: CalendarState, calendar_service: GoogleCalendarService
) -> CalendarState:
    try:
        user_input = state.get("user_input")
        context = state.get("context", {})

        itinerary_ids = []
        id_pattern = r"id가\s*(\d+(?:\s*,\s*\d+)*)"
        match = re.search(id_pattern, user_input)
        if match:
            numbers = match.group(1).replace(" ", "")
            itinerary_ids = [int(id) for id in numbers.split(",")]

        if not itinerary_ids:
            logger.warning("공유 요청이 있지만 일정 ID가 없음")
            response = (
                "일정을 먼저 생성해주세요. 그 후에 캘린더 기능을 사용할 수 있습니다."
            )
            return CalendarState(
                user_input=user_input,
                messages=state["messages"],
                context=context,
                response=response,
                next_node="calendar_node",
            )

        itineraries = Itinerary.objects.filter(id__in=itinerary_ids)
        response = ""
        for itinerary in itineraries:
            calendar_result = calendar_service.add_itinerary_to_calendar(itinerary)
            logger.info(f"캘린더 생성 완료: {len(response)} 글자")
            response += f"일정이 캘린더에 추가되었습니다. {calendar_result}"

        return CalendarState(
            user_input=user_input,
            messages=state["messages"],
            context=context,
            response=response,
            next_node="sharing_node",
            streaming={
                "message": response,
                "current_position": len(response),
                "is_complete": True,
            },
        )

    except Exception as e:
        logger.error(f"캘린더 노드 처리 오류: {str(e)}")
        logger.exception("전체 오류:")

        raise e
