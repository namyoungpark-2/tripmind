from tripmind.agents.place_search.types.place_search_state_type import PlaceSearchState
from tripmind.agents.place_search.utils.parser import parse_place_info


def ask_info_node(state: PlaceSearchState) -> PlaceSearchState:
    user_input = state.get("user_input", "")
    parsed_info = parse_place_info(state.get("user_input", ""))
    config_data = state.get("config_data", {})
    messages = state.get("messages", [])
    context = state.get("context", {})
    missing_info = []

    if not parsed_info["location"]:
        missing_info.append("어느 지역")

    if not parsed_info["category"]:
        missing_info.append("어떤 종류의 장소")

    if parsed_info["category"] == "맛집" and not parsed_info["subcategory"]:
        missing_info.append("어떤 종류의 음식")

    if missing_info:
        msg = f"더 정확한 추천을 위해 {', '.join(missing_info)}를 알려주실 수 있나요?"
        messages = messages + [{"role": "assistant", "content": msg}]

        return PlaceSearchState(
            user_input=user_input,
            config_data=config_data,
            messages=messages,
            parsed_info=parsed_info,
            context=context,
            next_node="place_search",
            streaming={
                "message": msg,
                "current_position": len(msg),
                "is_complete": True,
            },
        )
    else:
        return PlaceSearchState(
            user_input=user_input,
            config_data=config_data,
            messages=messages,
            parsed_info=parsed_info,
            context=context,
            next_node="place_search_node",
        )
