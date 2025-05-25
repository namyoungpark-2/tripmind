from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState
from tripmind.models.itinerary import Itinerary


def itinerary_list_node(state: ItineraryState) -> ItineraryState:
    user_id = state.get("config_data", {}).get("user_id", 1)
    itineraries = Itinerary.objects.all().filter(user=user_id).order_by("-date")

    response = ""
    for itinerary in itineraries:
        response += (
            f"id: {itinerary.id} 일정:{itinerary.title} - 장소:  {itinerary.destination} - 날짜: {itinerary.date.strftime('%Y-%m-%d')} "
            + "\n\n"
        )

    return ItineraryState(
        messages=state.get("messages", [])
        + [{"role": "assistant", "content": response}],
        context=state.get("context", {}),
        next_node="itinerary_list_node",
        response=response,
        streaming={
            "message": response,
            "current_position": len(response),
            "is_complete": True,
        },
    )
