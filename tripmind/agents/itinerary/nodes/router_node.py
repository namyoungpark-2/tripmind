from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState


def router_node(state: ItineraryState) -> ItineraryState:
    user_input = state.get("user_input", "")
    print("user_input : ", user_input)
    if "일정 목록" in user_input:
        state["next_node"] = "itinerary_list_node"
        print("next_node : ", state["next_node"])
        return state
    else:
        state["next_node"] = "ask_info_node"
        return state
