from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState
from tripmind.agents.itinerary.utils.extract_info import extract_travel_info


def ask_info_node(state: ItineraryState) -> ItineraryState:
    parsed_info = extract_travel_info(state.get("user_input", ""))
    messages = state.get("messages", [])
    context = state.get("context", {})
    missing_info = []

    if not parsed_info["destination"]:
        missing_info.append("어느 지역")

    if not parsed_info["duration"]:
        missing_info.append("여행 기간")

    for key, value in parsed_info.items():
        if value:
            context[key] = value

    # if len(missing_info) > 0:
    #     msg = f"여행 일정을 만들기 위해 {', '.join(missing_info)}에 대한 정보가 필요합니다. 알려주실 수 있나요? (ex: 서울지역 or 3박 4일 )"
    #     messages.append({"role": "assistant", "content": msg})
    #     return ItineraryState(
    #         messages=messages,
    #         context=context,
    #         next_node="ask_info_node",
    #         parsed_info=parsed_info,
    #         streaming={
    #             "message": msg,
    #             "current_position": len(msg),
    #             "is_complete": True,
    #         },
    #     )
    # else:
    return ItineraryState(
        messages=messages,
        context=context,
        next_node="itinerary_node",
        parsed_info=parsed_info,
    )
