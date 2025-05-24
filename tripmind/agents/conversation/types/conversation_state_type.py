from typing import List, Dict, Optional, Any

from tripmind.agents.common.types.base_state_type import BaseState


class ConversationState(BaseState):
    user_input: Optional[str]
    messages: List[Dict[str, str]]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    query: Optional[str]
    session_id: Optional[str]
    context: Optional[Dict[str, Any]]
    streaming: Optional[Dict[str, Any]]
