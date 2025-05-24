from tripmind.agents.prompt_router.types.prompt_router_state_type import (
    PromptRouterState,
)
from tripmind.agents.prompt_router.intent.manager import intent_pattern_manager


def input_node(state: PromptRouterState) -> PromptRouterState:
    user_input = state.get("user_input", "")
    context = state.get("context", {})
    print("user_input", user_input)
    print("state", state)

    state["messages"].append({"role": "user", "content": user_input})

    next_node = intent_pattern_manager.determine_intent_by_rule_based(user_input)

    updated_state_dict = {
        "user_input": user_input,
        "messages": state["messages"],
        "context": context,
        "response": user_input,
        "next_node": next_node,
        "intent": next_node,
    }

    updated_state = PromptRouterState(**updated_state_dict)
    return updated_state
