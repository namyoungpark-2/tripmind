from ..types.conversation_state_type import ConversationState


def router_node(state: ConversationState) -> ConversationState:
    """
    라우팅 노드
    """
    if not state.get("next_node"):
        state["next_node"] = "greeting"
    return state
