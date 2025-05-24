from typing import TypedDict, List, Dict, Optional, Any


class Streaming(TypedDict):
    message: str
    current_position: int
    is_complete: bool


class BaseState(TypedDict):
    user_input: str
    messages: List[Dict[str, str]]
    streaming: Optional[Streaming]
    next: Optional[str]
    next_node: Optional[str]
    intent: Optional[str]
    query: Optional[str]
    session_id: Optional[str]
    context: Optional[Dict[str, Any]]
    config_data: Optional[Dict[str, Any]]
    chat_history: Optional[List[Dict[str, Any]]]
