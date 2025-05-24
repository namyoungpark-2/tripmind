from typing import List, Dict, Optional, Any

from tripmind.agents.common.types.base_state_type import BaseState


class ItineraryState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    session_id: Optional[str]
    context: Optional[Dict[str, Any]]
    parsed_info: Optional[Dict[str, Any]]
    intermediate_steps: Optional[List[Dict[str, Any]]]
