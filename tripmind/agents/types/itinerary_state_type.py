from typing import Dict, List, Any, TypedDict


class ItineraryState(TypedDict, total=False):
    user_input: str
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    response: str
    next_action: str
    calendar_action: bool
    config_data: Dict[str, Any]
